import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import boto3
from botocore.config import Config
from google.cloud import resourcemanager_v3, securitycenter_v2
from google.protobuf.json_format import MessageToDict

try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.resource import SubscriptionClient
    from azure.mgmt.security import SecurityCenter
    from azure.mgmt.security.models import SecurityAssessmentResponse
except ImportError:  # allow using the file without Azure libs installed
    DefaultAzureCredential = SubscriptionClient = SecurityCenter = None
from cloudsecgpt.contexts.json_asff import JSONASFFContext
from cloudsecgpt.contexts.json_ocsf import JSONOCSFContext
from cloudsecgpt.utils.console import console


def default_org_if_single() -> str | None:
    crm = resourcemanager_v3.OrganizationsClient()
    orgs = list(crm.search_organizations(request={}))
    return orgs[0].name.split("/")[1] if len(orgs) == 1 else None


def load_findings_auto(
    path: str | Path,
    security_hub: bool = False,
    gcp_scc: str | None = None,
    azure_defender: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Decide automatically what to do:

    • --security-hub          → live pull from AWS Security Hub
    • --gcp-scc […]           → live pull from GCP SCC
    • --azure-defender […]    → live pull from Azure Defender
    • .parquet                → OCSF parquet
    • JSON with “Findings”    → ASFF
    • otherwise               → generic OCSF JSON
    """
    try:
        if security_hub:
            return fetch_findings_from_security_hub()
        if gcp_scc is not None:
            return fetch_findings_from_gcp_scc(gcp_scc)
        if azure_defender is not None:
            return fetch_findings_from_azure_defender(azure_defender)
        fp = Path(path)

        if fp.suffix.lower() == ".parquet":
            return JSONOCSFContext().load(fp)

        try:
            with fp.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            raise ValueError(f"Input file is not valid JSON/Parquet: {err}") from err

        if isinstance(data, dict) and "Findings" in data:
            return JSONASFFContext().load(fp)
        return JSONOCSFContext().load(fp)
    except Exception as e:
        console.log(f"[red]Error loading findings: {e}[/red]")
        return []


def fetch_findings_from_security_hub() -> List[Dict[str, Any]]:
    """
    Fetch findings from AWS Security Hub with a single-line status update
    """
    try:
        region = os.getenv("AWS_REGION", "us-east-1")
        client = boto3.client(
            "securityhub",
            region_name=region,
            config=Config(retries={"max_attempts": 3}),
        )
        all_findings = []
        next_token = None

        with console.status(
            "[green]Fetching findings from Security Hub…[/green]", spinner="dots"
        ) as status:
            page_num = 0
            while True:
                page_num += 1
                params = {
                    "Filters": {
                        "RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]
                    }
                }
                if next_token:
                    params["NextToken"] = next_token

                resp = client.get_findings(**params)
                batch = resp.get("Findings", [])
                all_findings.extend(batch)

                status.update(
                    f"[green]Fetching findings from Security Hub…[/green] [bold]{len(all_findings)} findings fetched[/bold]"
                )

                next_token = resp.get("NextToken")
                if not next_token:
                    break

        return JSONASFFContext().flatten_findings(all_findings)
    except Exception as e:
        console.log(f"[red]Error fetching findings from Security Hub: {e}[/red]")
        return []


def _resolve_scc_parent(raw: str | None) -> str:
    """
    Turn user input into the `parent` string SCC expects.

    * "" (empty)        → auto-detected single org
    * "123…"            → organizations/123…
    * "folders/456…"    → folders/456…
    * "projects/abc…"   → projects/abc…
    """
    try:
        if not raw:  # empty → auto with wildcard
            org = default_org_if_single()
            if not org:
                console.log(
                    "[red]Multiple organizations - please pass one with "
                    "--gcp-scc ORG_ID[/]"
                )
                sys.exit(1)
            raw_parent = f"organizations/{org}"
        elif raw.startswith(("organizations/", "folders/", "projects/")):
            raw_parent = raw
        elif raw.isdigit():
            raw_parent = f"organizations/{raw}"
        else:
            console.log(f"[red]Unrecognised --gcp-scc target: {raw}[/]")
            sys.exit(1)

        # now wildcard across *all* sources
        return f"{raw_parent}/sources/-"
    except Exception as e:
        console.log(f"[red]Error resolving SCC parent: {e}[/red]")
        return ""


def parse_gcp_scc_finding(
    findings: List[securitycenter_v2.Finding],
) -> List[Dict[str, Any]]:
    parsed_findings = []
    for finding in findings:
        parsed_findings.append(
            {
                "id": finding["name"].split("/")[-1],
                "title": finding["description"],
                "severity": finding["severity"].lower(),
                "description": finding["description"],
                "remediation_hint": finding.get("next_steps", ""),
                "provider": "gcp",
                "account_id": finding["resource_name"].split("/")[4],
                "region": (
                    "global"
                    if "/global" in finding["resource_name"]
                    else finding["resource_name"].split("/")[6]
                ),
                "resource_type": finding["resource_name"].split("/")[-2],
                "resource_uid": finding["resource_name"].split("/")[-1],
            }
        )
    return parsed_findings


def fetch_findings_from_gcp_scc(
    target_flag: str | None,
    *,
    filter_expr: str = 'state="ACTIVE"',
    page_size: int = 500,
) -> List[Dict[str, Any]]:
    """
    Fetch findings from GCP Security Command Center with a single-line status update.
    """
    try:
        parent = _resolve_scc_parent(target_flag)
        client = securitycenter_v2.SecurityCenterClient()
        all_findings: List[Dict[str, Any]] = []

        with console.status(
            "[green]Fetching findings from GCP SCC…[/green]", spinner="dots"
        ) as status:
            count = 0
            pager = client.list_findings(
                request={
                    "parent": parent,
                    "filter": filter_expr,
                    "page_size": page_size,
                }
            )
            for result in pager:
                finding_dict = MessageToDict(
                    result.finding._pb, preserving_proto_field_name=True
                )
                all_findings.append(finding_dict)

                count += 1
                status.update(
                    f"[green]Fetching findings from GCP SCC…[/green] "
                    f"[bold]{count} findings fetched[/bold]"
                )

        return parse_gcp_scc_finding(all_findings)

    except Exception as e:
        console.log(f"[red]Error fetching findings from GCP SCC: {e}[/red]")
        return []


def _default_sub_if_single() -> str | None:
    """
    If the account has exactly **one** subscription, return its ID – else None.
    """
    try:
        if not SubscriptionClient:
            return None
        subs = list(
            SubscriptionClient(credential=DefaultAzureCredential()).subscriptions.list()
        )
        return subs[0].subscription_id if len(subs) == 1 else None
    except Exception as e:
        console.log(f"[red]Error fetching subscriptions: {e}[/red]")
        return None


def _iter_azure_assessments(sub_id: str):
    """
    Yield Defender-for-Cloud assessments for a subscription
    (`subscriptions/<SUB_ID>` scope).
    """
    try:
        scope = f"subscriptions/{sub_id}"
        client = SecurityCenter(
            credential=DefaultAzureCredential(),
            subscription_id=sub_id,
        )

        for ass in client.assessments.list(scope=scope):
            if isinstance(ass, SecurityAssessmentResponse):
                yield ass
    except Exception as e:
        console.log(f"[red]Error fetching assessments: {e}[/red]")
        return []


def parse_azure_finding(ass: SecurityAssessmentResponse, sub_id: str) -> Dict[str, Any]:
    """Convert Azure Assessment → internal finding dict"""
    try:
        meta = ass.metadata
        details = ass.resource_details

        additional = getattr(details, "additional_properties", {}) or {}

        return {
            "id": ass.name,
            "title": ass.display_name,
            "severity": meta.severity.lower() if meta and meta.severity else "medium",
            "description": (
                meta.description
                if meta and getattr(meta, "description", None)
                else ass.display_name
            ),
            "remediation_hint": (
                meta.remediation_description
                if meta and getattr(meta, "remediation_description", None)
                else ""
            ),
            "provider": "azure",
            "account_id": sub_id,
            "region": additional.get("region", "Unknown"),
            "resource_type": additional.get("ResourceType", ""),
            "resource_uid": additional.get("ResourceId", ""),
        }
    except Exception as e:
        console.log(f"[red]Error parsing assessment: {e}[/red]")
        return {}


def fetch_findings_from_azure_defender(
    subscription_flag: str | None,
) -> List[Dict[str, Any]]:
    """
    Pull ACTIVE assessments from Azure Defender for Cloud.

    Args:
        subscription_flag:
            • ""     - auto-detect single subscription
            • "subId"
    """
    if DefaultAzureCredential is None:
        console.log(
            "[red]Azure SDK not installed - install azure-identity "
            "azure-mgmt-resource azure-mgmt-security[/]"
        )
        sys.exit(1)

    sub_id = subscription_flag or _default_sub_if_single()
    if not sub_id:
        console.log(
            "[red]Multiple subscriptions found - pass one with "
            "--azure-defender SUB_ID[/]"
        )
        sys.exit(1)

    findings: list[dict] = []
    with console.status(
        "[green]Fetching findings from Azure Defender…", spinner="dots"
    ):
        for ass in _iter_azure_assessments(sub_id):
            findings.append(parse_azure_finding(ass, sub_id))

    return findings
