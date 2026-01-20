"""Automatic insights generation for data analysis."""

import logging
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)


class AutoInsight:
    """Generate automatic insights and visualizations from DataFrames."""

    def __init__(
        self, dataframes: List[pd.DataFrame], names: Optional[List[str]] = None
    ):
        """Initialize AutoInsight with DataFrames.

        Args:
            dataframes: List of pandas DataFrames to analyze.
            names: Optional list of names for each DataFrame.
        """
        self.dataframes = dataframes
        self.names = names or [f"Dataset {i + 1}" for i in range(len(dataframes))]

    def generate_summary_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics for all DataFrames.

        Returns:
            Dict[str, Any]: Dictionary with statistics for each DataFrame.
        """
        summaries = {}

        for idx, (df, name) in enumerate(zip(self.dataframes, self.names)):
            summary = {
                "name": name,
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": df.dtypes.to_dict(),
                "numeric_summary": None,
                "missing_values": None,
                "categorical_summary": None,
            }

            # Reason: Numeric columns summary
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                summary["numeric_summary"] = df[numeric_cols].describe()

            # Reason: Missing values
            missing = df.isnull().sum()
            if missing.sum() > 0:
                summary["missing_values"] = missing[missing > 0]

            # Reason: Categorical columns summary
            categorical_cols = df.select_dtypes(include=["object", "category"]).columns
            if len(categorical_cols) > 0:
                cat_summary = {}
                for col in categorical_cols[:5]:  # Limit to 5 columns
                    cat_summary[col] = {
                        "unique_count": df[col].nunique(),
                        "top_values": df[col].value_counts().head(10).to_dict(),
                    }
                summary["categorical_summary"] = cat_summary

            summaries[name] = summary

        return summaries

    def generate_visualizations(self) -> List[Dict[str, Any]]:
        """Generate automatic visualizations for the data.

        Returns:
            List[Dict[str, Any]]: List of visualization objects with metadata.
        """
        visualizations = []

        # Reason: Close all existing figures to avoid memory warnings
        plt.close("all")

        for df, name in zip(self.dataframes, self.names):
            # Reason: Distribution plots for numeric columns
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if len(numeric_cols) > 0:
                # Limit to first 6 numeric columns
                for col in numeric_cols[:6]:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    df[col].hist(bins=30, ax=ax, edgecolor="black")
                    ax.set_title(f"Distribution of {col}")
                    ax.set_xlabel(col)
                    ax.set_ylabel("Frequency")
                    plt.tight_layout()

                    # Calculate interestingness score
                    variance_score = df[col].var() / (df[col].std() + 1e-10)
                    skewness = abs(df[col].skew()) if len(df[col].dropna()) > 0 else 0
                    score = variance_score + skewness * 10

                    visualizations.append(
                        {
                            "type": "histogram",
                            "title": f"{name} - Distribution of {col}",
                            "figure": fig,
                            "column": col,
                            "category": "distribution",
                            "score": float(score),
                        }
                    )

            # Reason: Bar charts for top categorical values
            categorical_cols = df.select_dtypes(
                include=["object", "category"]
            ).columns.tolist()
            if len(categorical_cols) > 0:
                # Limit to first 3 categorical columns
                for col in categorical_cols[:3]:
                    if (
                        df[col].nunique() <= 20
                    ):  # Only if reasonable number of categories
                        fig, ax = plt.subplots(figsize=(10, 6))
                        value_counts = df[col].value_counts().head(10)
                        value_counts.plot(kind="bar", ax=ax)
                        ax.set_title(f"Top 10 Values in {col}")
                        ax.set_xlabel(col)
                        ax.set_ylabel("Count")
                        plt.xticks(rotation=45, ha="right")
                        plt.tight_layout()

                        # Calculate interestingness score for categorical
                        entropy = -(
                            value_counts
                            / value_counts.sum()
                            * np.log2(value_counts / value_counts.sum() + 1e-10)
                        ).sum()
                        imbalance = value_counts.max() / value_counts.sum()
                        score = entropy + (1 - imbalance) * 5

                        visualizations.append(
                            {
                                "type": "bar",
                                "title": f"{name} - Top Values in {col}",
                                "figure": fig,
                                "column": col,
                                "category": "categorical",
                                "score": float(score),
                            }
                        )

            # Reason: Detect and visualize time-series trends
            date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
            # Also check for columns that might be dates but stored as strings
            for col in df.select_dtypes(include=["object"]).columns:
                try:
                    pd.to_datetime(df[col], errors="raise")
                    date_cols.append(col)
                except (ValueError, TypeError):
                    pass

            if len(date_cols) > 0 and len(numeric_cols) > 0:
                # Show trends for up to 2 numeric columns over time
                date_col = date_cols[0]
                df_time = df.copy()
                if df_time[date_col].dtype == "object":
                    df_time[date_col] = pd.to_datetime(df_time[date_col])

                for num_col in numeric_cols[:2]:
                    fig, ax = plt.subplots(figsize=(12, 6))
                    df_sorted = df_time.sort_values(date_col)
                    ax.plot(
                        df_sorted[date_col], df_sorted[num_col], marker="o", linewidth=2
                    )
                    ax.set_title(f"Trend of {num_col} over {date_col}")
                    ax.set_xlabel(date_col)
                    ax.set_ylabel(num_col)
                    plt.xticks(rotation=45, ha="right")
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()

                    # Calculate trend score
                    try:
                        from scipy import stats

                        x_numeric = (
                            df_sorted[date_col] - df_sorted[date_col].min()
                        ).dt.total_seconds()
                        slope, _, r_value, _, _ = stats.linregress(
                            x_numeric, df_sorted[num_col].fillna(0)
                        )
                        trend_score = abs(r_value) * 30
                    except Exception:
                        trend_score = 10.0

                    visualizations.append(
                        {
                            "type": "line",
                            "title": f"{name} - Trend of {num_col}",
                            "figure": fig,
                            "column": num_col,
                            "category": "trending",
                            "score": float(trend_score),
                        }
                    )

            # Reason: Correlation heatmap if multiple numeric columns
            if len(numeric_cols) > 1:
                fig, ax = plt.subplots(figsize=(12, 10))
                # Limit to first 10 numeric columns for readability
                cols_to_plot = numeric_cols[:10]
                corr = df[cols_to_plot].corr()
                sns.heatmap(
                    corr,
                    annot=True,
                    fmt=".2f",
                    cmap="coolwarm",
                    ax=ax,
                    center=0,
                    square=True,
                    xticklabels=corr.columns,
                    yticklabels=corr.columns,
                    cbar_kws={"shrink": 0.8},
                )
                ax.set_title("Correlation Matrix", pad=20)
                # Rotate labels for better readability
                plt.xticks(rotation=45, ha="right")
                plt.yticks(rotation=0)
                plt.tight_layout()

                # Calculate interestingness score for correlation
                corr_values = corr.values[np.triu_indices_from(corr.values, k=1)]
                max_corr = np.max(np.abs(corr_values)) if len(corr_values) > 0 else 0
                avg_corr = np.mean(np.abs(corr_values)) if len(corr_values) > 0 else 0
                score = max_corr * 50 + avg_corr * 20

                visualizations.append(
                    {
                        "type": "heatmap",
                        "title": f"{name} - Correlation Matrix",
                        "figure": fig,
                        "column": None,
                        "category": "correlation",
                        "score": float(score),
                    }
                )

        return visualizations

    def generate_insights_text(self, summaries: Dict[str, Any]) -> str:
        """Generate natural language insights from summaries.

        Args:
            summaries: Dictionary of summary statistics.

        Returns:
            str: Markdown-formatted insights text.
        """
        insights = ["# 📊 Auto-Generated Data Insights\n"]

        for name, summary in summaries.items():
            insights.append(f"## {summary['name']}\n")

            # Reason: Basic info
            rows, cols = summary["shape"]
            insights.append(f"**Shape**: {rows:,} rows × {cols} columns\n")

            # Reason: Missing values
            if summary["missing_values"] is not None:
                insights.append("\n**⚠️ Missing Values Found:**")
                for col, count in summary["missing_values"].items():
                    pct = (count / rows) * 100
                    insights.append(f"- `{col}`: {count:,} ({pct:.1f}%)")
                insights.append("")

            # Reason: Numeric summary
            if summary["numeric_summary"] is not None:
                numeric_cols = summary["numeric_summary"].columns.tolist()
                insights.append(f"\n**📈 Numeric Columns ({len(numeric_cols)}):**")
                insights.append(
                    f"{', '.join([f'`{col}`' for col in numeric_cols[:10]])}"
                )
                if len(numeric_cols) > 10:
                    insights.append(f"... and {len(numeric_cols) - 10} more")
                insights.append("")

            # Reason: Categorical summary
            if summary["categorical_summary"]:
                insights.append("\n**📋 Categorical Columns:**")
                for col, info in summary["categorical_summary"].items():
                    insights.append(f"- `{col}`: {info['unique_count']} unique values")
                    top_val = list(info["top_values"].keys())[0]
                    top_count = info["top_values"][top_val]
                    insights.append(
                        f"  - Most frequent: `{top_val}` ({top_count} times)"
                    )
                insights.append("")

            insights.append("---\n")

        return "\n".join(insights)

    def generate_full_report(self) -> Dict[str, Any]:
        """Generate a complete auto-insights report.

        Returns:
            Dict[str, Any]: Complete report with text insights and visualizations.
        """
        summaries = self.generate_summary_statistics()
        visualizations = self.generate_visualizations()
        insights_text = self.generate_insights_text(summaries)

        # Sort visualizations by score (highest first)
        visualizations_sorted = sorted(
            visualizations, key=lambda x: x.get("score", 0), reverse=True
        )

        # Organize by category
        viz_by_category = {
            "trending": [],
            "correlation": [],
            "distribution": [],
            "categorical": [],
        }

        for viz in visualizations_sorted:
            category = viz.get("category", "distribution")
            viz_by_category[category].append(viz)

        return {
            "insights_text": insights_text,
            "visualizations": visualizations_sorted,
            "visualizations_by_category": viz_by_category,
            "summaries": summaries,
        }
