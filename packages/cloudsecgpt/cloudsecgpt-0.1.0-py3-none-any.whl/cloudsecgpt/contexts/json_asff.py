"""
ASFF (AWS Security Finding Format) context loader.

* Accepts native Security Hub export files (JSON, compressed JSON is handled
  by `Path.read_text()` transparently when caller un-gzips first).
* Returns a `List[dict]` ready for the normalization step.

The loader does **only minimal massaging** – it flattens the top-level
“Findings” wrapper and copies a few frequently-used attributes to short names
so that `normalize_finding()` can detect them easily:

    {
        "id": ...,
        "title": ...,
        "description": ...,
        "severity_id": <0-10>,
        "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
        "resources": [ {"type": "...", "uid": "..."} ],
        "cloud": { "provider": "aws", "account": { "uid": "…" }, "region": "…" },
        # + the rest of the original ASFF dict under "raw"
    }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class JSONASFFContext:
    """Loads AWS Security Hub findings in ASFF format."""

    def flatten_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        flattened_findings = []
        for f in findings:
            sev_label: str = f.get("Severity", {}).get("Label") or f.get(
                "FindingProviderFields", {}
            ).get("Severity", {}).get("Label", "")

            for r in f.get("Resources", []):
                flattened_findings.append(
                    {
                        "id": f.get("Id"),
                        "title": f.get("Title"),
                        "description": f.get("Description"),
                        "severity": sev_label.lower(),
                        "resource_type": r.get("Type"),
                        "resource_uid": r.get("Id"),
                        "provider": "aws",
                        "account_id": f.get("AwsAccountId"),
                        "region": f.get("Region"),
                        "remediation_hint": f.get("Remediation", {})
                        .get("Recommendation", {})
                        .get("Url", ""),
                        # keep original ASFF for anything else we may need later
                        "asff_raw": f,
                    }
                )
        return flattened_findings

    # --------------------------------------------------------------------- #

    def load(self, path: str | Path) -> List[Dict[str, Any]]:
        """
        Read a `.json` (potentially the large Security Hub export) and return
        a list of flattened finding dicts.
        """
        fp = Path(path)
        data = json.loads(fp.read_text())
        findings = data.get("Findings") if isinstance(data, dict) else data

        if not isinstance(findings, list):
            raise ValueError("ASFF file does not contain a 'Findings' array")
        return self.flatten_findings(findings)
