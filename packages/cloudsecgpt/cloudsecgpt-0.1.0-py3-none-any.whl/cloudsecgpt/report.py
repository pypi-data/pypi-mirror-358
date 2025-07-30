from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from cloudsecgpt.utils.console import console
from cloudsecgpt.utils.files import ANALYZED_FILENAME, BASE64_LOGO, GROUPED_FILENAME


def _safe_split_resources(resources_value):
    """Safely split resources string, handling NaN and None values.

    This function handles the case where pandas reads empty or NaN values
    in the resources column as floats instead of strings, which would cause
    an AttributeError when trying to call .split() on a float.
    """
    if pd.isna(resources_value) or resources_value is None:
        return []
    return [r.strip() for r in str(resources_value).split(",") if r.strip()]


def generate_report(input_path: str | Path, output_path: str | Path):
    try:
        # --------------------------------------------------------------------- #
        # 1) Load data
        # --------------------------------------------------------------------- #
        p = Path(input_path)
        df = pd.read_csv(p / ANALYZED_FILENAME)

        # --------------------------------------------------------------------- #
        # 2) Metrics for charts and stats
        # --------------------------------------------------------------------- #
        total = len(df)

        # Risk-score histogram
        by_score = df["risk_score"].value_counts().sort_index()
        score_labels = [int(s) for s in by_score.index]
        score_counts = [int(c) for c in by_score.values]

        # Resource-type distribution
        by_resource = df["resource_type"].value_counts()
        resource_labels = by_resource.index.tolist()
        resource_counts = by_resource.values.tolist()

        # --------------------------------------------------------------------- #
        # 3) Top 10 findings
        # --------------------------------------------------------------------- #
        top10 = df.sort_values("risk_score", ascending=False).head(10)

        # --------------------------------------------------------------------- #
        # 4) Clusters (optional)
        # --------------------------------------------------------------------- #
        cluster_csv = p / GROUPED_FILENAME
        if cluster_csv.exists():
            # Read CSV with explicit dtype for resources column to avoid float conversion
            # when the column contains empty values or NaN
            groups = pd.read_csv(cluster_csv, dtype={"resources": str})
        else:
            groups = pd.DataFrame()

        # --------------------------------------------------------------------- #
        # 5) Render template
        # --------------------------------------------------------------------- #
        env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"),
            autoescape=select_autoescape(
                enabled_extensions=("html", "xml"),
                default_for_string=True,
                default=True,
            ),
        )
        tpl = env.get_template("report.html.j2")
        html = tpl.render(
            # summary cards
            total=total,
            # bar chart
            score_labels=score_labels,
            score_counts=score_counts,
            # pie chart
            resource_labels=resource_labels,
            resource_counts=resource_counts,
            # tables
            top10=top10.to_dict(orient="records"),
            groups=[
                {
                    **row,
                    "resources": _safe_split_resources(row["resources"]),
                }
                for row in groups.to_dict(orient="records")
            ],
            logo_base64=BASE64_LOGO,
        )

        Path(output_path).write_text(html)
    except Exception as e:
        console.log(f"[red]Error generating report: {e}[/red]")
        raise
