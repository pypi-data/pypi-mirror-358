import csv
import sys
from typing import Any, Dict, List

from cloudsecgpt.utils.console import console


class TriageProtocol:
    """
    Builds single-batch prompts (including IDs) and parses lines id|score|summary|fix.
    """

    SYSTEM = """
You are **CloudSecGPT**, a senior cloud-security analyst.

Analyse each finding block and output **only the risky ones** as **one single line** in the form:

id|score|summary|why|cli_fix|fix

──────────────────────── STRICT FORMAT ────────────────────────
Exactly **5** pipe characters "|" → 6 fields total.
**Field-1** id       → identical to the input (full Finding ID string).
**Field-2** score    → the digits **1-10 only** (no words, no spaces).
**Field-3** summary  → ≤ 120 chars, one sentence, no resource names.
**Field-4** why      → ≤ 120 chars, impact in business/tech terms.
**Field-5** cli_fix → one-line shell / CLI command (no "|").
**Field-6** fix      → concise remediation (imperative verb).
Never write labels like "ID:" or the word "score".
Never add leading/trailing spaces.
Never add extra lines, headers, bullets or prose.
Never use the "|" character inside a field.

──────────────────────── EXAMPLES ─────────────────────────────
finding/1234567890|9|S3 bucket allows public READ access|Public objects may leak sensitive data|aws s3api put-bucket-acl --acl private --bucket myBucket|Restrict bucket ACL to private

──────────────────── VALIDATE BEFORE YOU SPEAK ───────────────
1. Think silently to decide if the finding is risky.
2. Construct the line in your mind.
3. Check it matches this regex exactly:
   `^[^|]+\\|(10|[1-9])\\|[^|]+\\|[^|]+\\|[^|]+\\|[^|]+$`
4. If it doesn't, FIX it before answering.
5. If no findings are risky, output **nothing**.
6. Do not replicate the input format.

When you're 100% sure, output the lines in the mentioned format "id|score|summary|why|cli_fix|fix" on the next line **only after the marker**:

BEGIN
"""

    def build_prompt(self, findings: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        try:
            user_sections = []
            for f in findings:
                user_sections.append(
                    f"ID: {f['id']}\n"
                    f"Provider: {f['provider']}\n"
                    f"Account ID: {f['account_id']}\n"
                    f"Region: {f['region']}\n"
                    f"Resource Type: {f['resource_type']}\n"
                    f"Resource UID: {f['resource_uid']}\n"
                    f"Finding: {f['title']}\n"
                    f"Severity: {f['severity']}\n"
                    f"Details: {f['description']}\n"
                    f"Hint: {f.get('remediation_hint', '')}"
                )
            user_content = "\n\n".join(user_sections)
            return [
                {"role": "system", "content": self.SYSTEM},
                {"role": "user", "content": user_content},
            ]
        except Exception as e:
            console.log(f"[red]Error building prompt: {e}")
            sys.exit(1)

    def parse_response(self, text: str) -> List[Dict[str, Any]]:
        try:
            rows: List[Dict[str, Any]] = []
            for line in text.splitlines():
                try:
                    if line.startswith("id|score|summary|why|cli_fix|fix"):
                        continue
                    parts = [p.strip() for p in line.split("|", 5)]
                    if len(parts) != 6:
                        continue
                    fid, raw_score, summary, why, cli_fix, fix = parts

                    try:
                        score = int(raw_score)
                    except Exception:
                        continue

                    rows.append(
                        {
                            "id": fid,
                            "risk_score": score,
                            "summary": summary,
                            "why": why,
                            "cli_fix": cli_fix,
                            "remediation": fix,
                        }
                    )
                except Exception as e:
                    console.log(f"[red]Error parsing line: {e}[/red]")
                    continue
            return rows
        except Exception as e:
            console.log(f"[red]Error parsing response: {e}")
            return []

    def write_csv(self, rows: List[Dict[str, Any]], out_path: str):
        try:
            if not rows:
                # nothing to write
                return
            with open(out_path, "w", newline="") as fp:
                writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
        except Exception as e:
            console.log(f"[red]Error writing CSV: {e}")
            return
