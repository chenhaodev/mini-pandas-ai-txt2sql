"""Deep insights generator that creates and tests hypotheses about data."""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DeepInsightGenerator:
    """Generate deep insights by creating and testing hypotheses about data.

    This class analyzes data structure, generates intelligent hypotheses,
    and tests each hypothesis to provide data-driven insights.
    """

    def __init__(
        self, dataframes: List[pd.DataFrame], names: Optional[List[str]] = None
    ):
        """Initialize the deep insight generator.

        Args:
            dataframes: List of pandas DataFrames to analyze.
            names: Optional list of names for each DataFrame.
        """
        self.dataframes = dataframes
        self.names = names or [f"Dataset {i + 1}" for i in range(len(dataframes))]

    def analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the structure of a DataFrame to inform hypothesis generation.

        Args:
            df: The DataFrame to analyze.

        Returns:
            Dict containing column types and statistics.
        """
        structure = {
            "numeric_cols": df.select_dtypes(include=["number"]).columns.tolist(),
            "categorical_cols": df.select_dtypes(
                include=["object", "category"]
            ).columns.tolist(),
            "datetime_cols": df.select_dtypes(include=["datetime64"]).columns.tolist(),
            "row_count": len(df),
            "col_count": len(df.columns),
        }

        # Identify potential ID columns (high cardinality)
        structure["id_cols"] = [
            col
            for col in structure["numeric_cols"]
            if df[col].nunique() > len(df) * 0.9
        ]

        # Identify potential grouping columns (low cardinality categorical)
        structure["grouping_cols"] = [
            col
            for col in structure["categorical_cols"]
            if 2 <= df[col].nunique() <= 20
        ]

        # Identify potential metric columns (numeric, not IDs)
        structure["metric_cols"] = [
            col
            for col in structure["numeric_cols"]
            if col not in structure["id_cols"]
        ]

        return structure

    def generate_hypotheses(
        self, df: pd.DataFrame, structure: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate hypotheses based on data structure.

        Args:
            df: The DataFrame to analyze.
            structure: The data structure analysis.

        Returns:
            List of hypothesis dictionaries with query functions.
        """
        hypotheses = []

        # Hypothesis 1: Distribution of key metrics
        if structure["metric_cols"]:
            col = structure["metric_cols"][0]
            hypotheses.append(
                {
                    "id": 1,
                    "title": f"Distribution Analysis of '{col}'",
                    "description": f"What is the distribution of {col}? Are there outliers?",
                    "query_type": "distribution",
                    "column": col,
                }
            )

        # Hypothesis 2: Group comparison
        if structure["grouping_cols"] and structure["metric_cols"]:
            group_col = structure["grouping_cols"][0]
            metric_col = structure["metric_cols"][0]
            hypotheses.append(
                {
                    "id": 2,
                    "title": f"Comparison by '{group_col}'",
                    "description": f"How does {metric_col} vary across different {group_col}?",
                    "query_type": "group_comparison",
                    "group_col": group_col,
                    "metric_col": metric_col,
                }
            )

        # Hypothesis 3: Top/Bottom analysis
        if structure["metric_cols"] and len(df) > 5:
            col = structure["metric_cols"][0]
            hypotheses.append(
                {
                    "id": 3,
                    "title": f"Top & Bottom Analysis for '{col}'",
                    "description": f"What are the top and bottom performers by {col}?",
                    "query_type": "top_bottom",
                    "column": col,
                }
            )

        # Hypothesis 4: Correlation analysis
        if len(structure["metric_cols"]) >= 2:
            col1, col2 = structure["metric_cols"][:2]
            hypotheses.append(
                {
                    "id": 4,
                    "title": f"Correlation between '{col1}' and '{col2}'",
                    "description": f"Is there a relationship between {col1} and {col2}?",
                    "query_type": "correlation",
                    "columns": [col1, col2],
                }
            )

        # Hypothesis 5: Missing data analysis
        missing_cols = [col for col in df.columns if df[col].isna().sum() > 0]
        if missing_cols:
            hypotheses.append(
                {
                    "id": 5,
                    "title": "Missing Data Pattern Analysis",
                    "description": "Where is data missing and what patterns exist?",
                    "query_type": "missing_data",
                    "columns": missing_cols[:5],
                }
            )

        # Hypothesis 6: Category distribution (if no missing data hypothesis)
        if len(hypotheses) < 5 and structure["grouping_cols"]:
            col = structure["grouping_cols"][0]
            hypotheses.append(
                {
                    "id": len(hypotheses) + 1,
                    "title": f"Category Distribution of '{col}'",
                    "description": f"What is the distribution of categories in {col}?",
                    "query_type": "category_distribution",
                    "column": col,
                }
            )

        return hypotheses[:5]  # Limit to 5 hypotheses

    def test_hypothesis(
        self, df: pd.DataFrame, hypothesis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test a hypothesis by executing the appropriate query.

        Args:
            df: The DataFrame to query.
            hypothesis: The hypothesis to test.

        Returns:
            Dict with hypothesis results.
        """
        result = {
            "hypothesis": hypothesis,
            "success": False,
            "finding": None,
            "data": None,
        }

        try:
            query_type = hypothesis["query_type"]

            if query_type == "distribution":
                col = hypothesis["column"]
                stats = df[col].describe()
                skewness = df[col].skew() if len(df[col].dropna()) > 2 else 0
                result["finding"] = self._format_distribution_finding(
                    col, stats, skewness
                )
                result["data"] = stats.to_dict()
                result["success"] = True

            elif query_type == "group_comparison":
                group_col = hypothesis["group_col"]
                metric_col = hypothesis["metric_col"]
                grouped = df.groupby(group_col)[metric_col].agg(["mean", "count"])
                grouped = grouped.sort_values("mean", ascending=False)
                result["finding"] = self._format_group_comparison_finding(
                    group_col, metric_col, grouped
                )
                result["data"] = grouped.head(10).to_dict()
                result["success"] = True

            elif query_type == "top_bottom":
                col = hypothesis["column"]
                # Get identifier column if available
                id_cols = [c for c in df.columns if "name" in c.lower() or "id" in c.lower()]
                display_col = id_cols[0] if id_cols else df.columns[0]
                top5 = df.nlargest(5, col)[[display_col, col]]
                bottom5 = df.nsmallest(5, col)[[display_col, col]]
                result["finding"] = self._format_top_bottom_finding(
                    col, top5, bottom5, display_col
                )
                result["data"] = {"top": top5.to_dict(), "bottom": bottom5.to_dict()}
                result["success"] = True

            elif query_type == "correlation":
                cols = hypothesis["columns"]
                corr = df[cols[0]].corr(df[cols[1]])
                result["finding"] = self._format_correlation_finding(
                    cols[0], cols[1], corr
                )
                result["data"] = {"correlation": corr}
                result["success"] = True

            elif query_type == "missing_data":
                cols = hypothesis["columns"]
                missing_stats = {col: df[col].isna().sum() for col in cols}
                total_rows = len(df)
                result["finding"] = self._format_missing_data_finding(
                    missing_stats, total_rows
                )
                result["data"] = missing_stats
                result["success"] = True

            elif query_type == "category_distribution":
                col = hypothesis["column"]
                dist = df[col].value_counts()
                result["finding"] = self._format_category_finding(col, dist)
                result["data"] = dist.head(10).to_dict()
                result["success"] = True

        except Exception as e:
            logger.warning(f"Failed to test hypothesis: {e}")
            result["finding"] = f"Could not test this hypothesis: {str(e)}"

        return result

    def _format_distribution_finding(
        self, col: str, stats: pd.Series, skewness: float
    ) -> str:
        """Format distribution analysis finding."""
        skew_desc = "normally distributed"
        if skewness > 1:
            skew_desc = "right-skewed (tail towards higher values)"
        elif skewness < -1:
            skew_desc = "left-skewed (tail towards lower values)"

        return (
            f"**{col}** ranges from {stats['min']:.2f} to {stats['max']:.2f} "
            f"with mean {stats['mean']:.2f} and median {stats['50%']:.2f}. "
            f"The distribution is {skew_desc}."
        )

    def _format_group_comparison_finding(
        self, group_col: str, metric_col: str, grouped: pd.DataFrame
    ) -> str:
        """Format group comparison finding."""
        top_group = grouped.index[0]
        top_mean = grouped.iloc[0]["mean"]
        bottom_group = grouped.index[-1]
        bottom_mean = grouped.iloc[-1]["mean"]

        diff_pct = ((top_mean - bottom_mean) / bottom_mean * 100) if bottom_mean else 0

        return (
            f"**{group_col}** shows significant variation in {metric_col}. "
            f"'{top_group}' has the highest average ({top_mean:.2f}), "
            f"while '{bottom_group}' has the lowest ({bottom_mean:.2f}). "
            f"Difference: {diff_pct:.1f}%."
        )

    def _format_top_bottom_finding(
        self, col: str, top5: pd.DataFrame, bottom5: pd.DataFrame, display_col: str
    ) -> str:
        """Format top/bottom analysis finding."""
        top_items = [
            f"{row[display_col]} ({row[col]:.2f})" for _, row in top5.iterrows()
        ]
        bottom_items = [
            f"{row[display_col]} ({row[col]:.2f})" for _, row in bottom5.iterrows()
        ]

        return (
            f"**Top 5 by {col}**: {', '.join(top_items[:3])}...\n"
            f"**Bottom 5 by {col}**: {', '.join(bottom_items[:3])}..."
        )

    def _format_correlation_finding(
        self, col1: str, col2: str, corr: float
    ) -> str:
        """Format correlation finding."""
        strength = "no"
        if abs(corr) > 0.7:
            strength = "strong"
        elif abs(corr) > 0.4:
            strength = "moderate"
        elif abs(corr) > 0.2:
            strength = "weak"

        direction = "positive" if corr > 0 else "negative"

        return (
            f"There is a **{strength} {direction} correlation** (r={corr:.3f}) "
            f"between {col1} and {col2}."
        )

    def _format_missing_data_finding(
        self, missing_stats: Dict[str, int], total_rows: int
    ) -> str:
        """Format missing data finding."""
        findings = []
        for col, count in missing_stats.items():
            pct = (count / total_rows) * 100
            findings.append(f"- **{col}**: {count} missing ({pct:.1f}%)")

        return "Missing data found:\n" + "\n".join(findings)

    def _format_category_finding(self, col: str, dist: pd.Series) -> str:
        """Format category distribution finding."""
        total = dist.sum()
        top_cat = dist.index[0]
        top_pct = (dist.iloc[0] / total) * 100

        return (
            f"**{col}** has {len(dist)} unique categories. "
            f"Most common: '{top_cat}' ({top_pct:.1f}% of total). "
            f"Distribution: {dict(list(dist.head(5).items()))}"
        )

    def generate_deep_insights(self) -> Dict[str, Any]:
        """Generate deep insights by testing multiple hypotheses.

        Returns:
            Dict containing insights text and hypothesis results.
        """
        all_results = []
        insights_text = ["# Deep Data Insights\n"]
        insights_text.append(
            "_Generated by analyzing data structure and testing hypotheses_\n"
        )

        for df, name in zip(self.dataframes, self.names):
            insights_text.append(f"\n## {name}\n")

            # Analyze structure
            structure = self.analyze_data_structure(df)
            insights_text.append(
                f"**Dataset**: {structure['row_count']:,} rows × "
                f"{structure['col_count']} columns\n"
            )

            # Generate and test hypotheses
            hypotheses = self.generate_hypotheses(df, structure)

            if not hypotheses:
                insights_text.append(
                    "_Could not generate hypotheses for this dataset._\n"
                )
                continue

            insights_text.append(f"\n### Testing {len(hypotheses)} Hypotheses\n")

            for hypothesis in hypotheses:
                result = self.test_hypothesis(df, hypothesis)
                all_results.append(result)

                # Format as expandable section
                status = "✅" if result["success"] else "❌"
                insights_text.append(
                    f"\n#### {status} Hypothesis {hypothesis['id']}: "
                    f"{hypothesis['title']}\n"
                )
                insights_text.append(f"_{hypothesis['description']}_\n\n")

                if result["finding"]:
                    insights_text.append(f"{result['finding']}\n")

            insights_text.append("\n---\n")

        return {
            "insights_text": "\n".join(insights_text),
            "hypotheses_results": all_results,
            "hypothesis_count": len(all_results),
            "successful_count": sum(1 for r in all_results if r["success"]),
        }
