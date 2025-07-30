import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from cloudsecgpt.utils.console import console


class JSONOCSFContext:
    """Loads and lightly normalizes JSON-OCSF findings, supporting JSON and Parquet formats."""

    _SEVERITY_LABEL = {
        0: "unknown",
        1: "informational",
        2: "low",
        3: "medium",
        4: "high",
        5: "critical",
        6: "fatal",
    }

    def _safe(self, obj: dict, path: str, default=""):
        try:
            cur = obj
            for key in path.split("."):
                if not isinstance(cur, dict) or key not in cur:
                    return default
                cur = cur[key]
            return cur
        except Exception as e:
            console.log(f"[red]Error normalizing finding: {e}[/red]")
            return {}

    def parse_json_ocsf(self, f: Dict[str, Any], idx: int) -> Dict[str, Any]:
        try:
            # Only support Detection Findings or Compliance Findings
            if (
                f.get("class_name") != "Detection Finding"
                and f.get("class_name") != "Compliance Finding"
            ):
                return {}
            fid = (
                self._safe(f, "finding_info.uid")
                or f.get("finding_uid")
                or self._safe(f, "metadata.event_code")
                or str(idx)
            )
            title = self._safe(f, "finding_info.title") or f.get(
                "message", "Untitled finding"
            )
            description = (
                f.get("message")
                or self._safe(f, "finding_info.desc")
                or f.get("description", "")
            )
            try:
                sev_raw = f.get("severity_id")
                severity = self._SEVERITY_LABEL.get(int(sev_raw), "medium")
            except Exception:
                severity = "medium"
            remediation_hint = self._safe(f, "remediation.desc")
            provider = self._safe(f, "cloud.provider") or self._safe(
                f, "metadata.vendor_name"
            )
            account_id = self._safe(f, "cloud.account.uid") or self._safe(
                f, "cloud.account.id"
            )
            project_id = self._safe(f, "cloud.project.id")
            subscription = self._safe(f, "cloud.subscription.id")
            account = account_id or project_id or subscription or ""
            region = self._safe(f, "cloud.region")

            resource_type = ""
            resource_uid = ""
            resources = f.get("resources")
            if resources:
                if isinstance(resources, list):
                    resource_type = (
                        resources[0].get("type")
                        if resources[0].get("type")
                        else "Unknown"
                    )
                    resource_uid = (
                        resources[0].get("uid")
                        if resources[0].get("uid")
                        else (
                            resources[0].get("name")
                            if resources[0].get("name")
                            else "Unknown"
                        )
                    )
            elif "resource" in f:
                resource_type = f["resource"].get("type", "Unknown")
                resource_uid = f["resource"].get("uid", "Unknown")
            return {
                "id": fid,
                "title": title,
                "severity": severity,
                "description": description,
                "remediation_hint": remediation_hint,
                "provider": provider,
                "account_id": account,
                "region": region,
                "resource_type": resource_type,
                "resource_uid": resource_uid,
            }
        except Exception as e:
            console.log(f"[red]Error normalizing finding: {e}[/red]")
            return {}

    def load(self, path: str) -> List[Dict[str, Any]]:
        try:
            fp = Path(path)
            # Parquet support for large-scale exports (e.g., AWS Security Lake)
            if fp.suffix.lower() == ".parquet":
                # Read Parquet into DataFrame and convert to list of dicts
                df = pd.read_parquet(fp)
                df = df.where(pd.notnull(df), None)
                records = df.to_dict(orient="records")

                def _convert(val: Any) -> Any:
                    if isinstance(val, np.generic):
                        return val.item()
                    if isinstance(val, np.ndarray):
                        return val.tolist()
                    return val

                return [
                    self.parse_json_ocsf({k: _convert(v) for k, v in rec.items()}, idx)
                    for idx, rec in enumerate(records, 1)
                ]

            # Fallback to JSON-based loader
            text = fp.read_text()
            data = json.loads(text)
            if isinstance(data, dict) and "findings" in data:
                return [
                    self.parse_json_ocsf(f, idx)
                    for idx, f in enumerate(data["findings"], 1)
                ]
            return [self.parse_json_ocsf(f, idx) for idx, f in enumerate(data, 1)]
        except Exception as e:
            console.log(f"[red]JSONOCSFContext error: {e}[/red]")
            sys.exit(1)
