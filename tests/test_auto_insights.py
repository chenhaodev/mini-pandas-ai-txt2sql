"""Unit tests for auto insights module."""

import matplotlib
import pandas as pd
import pytest

from src.auto_insights import AutoInsight


class TestAutoInsight:
    """Tests for AutoInsight class."""

    @pytest.fixture
    def sample_numeric_df(self):
        """Create sample DataFrame with numeric data."""
        return pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50],
                "C": [100, 200, 300, 400, 500],
            }
        )

    @pytest.fixture
    def sample_categorical_df(self):
        """Create sample DataFrame with categorical data."""
        return pd.DataFrame(
            {
                "Category": ["A", "B", "A", "C", "B", "A", "C", "A"],
                "Value": [1, 2, 3, 4, 5, 6, 7, 8],
            }
        )

    @pytest.fixture
    def sample_mixed_df(self):
        """Create sample DataFrame with mixed data types."""
        return pd.DataFrame(
            {
                "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                "Age": [25, 30, 35, 40, 45],
                "City": ["NY", "LA", "NY", "SF", "LA"],
                "Salary": [50000, 60000, 70000, 80000, 90000],
            }
        )

    def test_initialization(self, sample_numeric_df):
        """Test AutoInsight initialization."""
        insight = AutoInsight([sample_numeric_df])

        assert len(insight.dataframes) == 1
        assert len(insight.names) == 1
        assert insight.names[0] == "Dataset 1"

    def test_initialization_with_names(self, sample_numeric_df):
        """Test AutoInsight initialization with custom names."""
        insight = AutoInsight([sample_numeric_df], names=["My Dataset"])

        assert insight.names[0] == "My Dataset"

    def test_generate_summary_statistics_numeric(self, sample_numeric_df):
        """Test summary statistics generation for numeric data."""
        insight = AutoInsight([sample_numeric_df])
        summaries = insight.generate_summary_statistics()

        assert len(summaries) == 1
        summary = summaries["Dataset 1"]

        assert summary["shape"] == (5, 3)
        assert len(summary["columns"]) == 3
        assert summary["numeric_summary"] is not None
        assert "A" in summary["numeric_summary"].columns

    def test_generate_summary_statistics_categorical(self, sample_categorical_df):
        """Test summary statistics generation for categorical data."""
        insight = AutoInsight([sample_categorical_df])
        summaries = insight.generate_summary_statistics()

        summary = summaries["Dataset 1"]

        assert summary["categorical_summary"] is not None
        assert "Category" in summary["categorical_summary"]
        assert summary["categorical_summary"]["Category"]["unique_count"] == 3

    def test_generate_summary_statistics_missing_values(self):
        """Test missing values detection."""
        df = pd.DataFrame(
            {
                "A": [1, 2, None, 4, 5],
                "B": [10, None, None, 40, 50],
            }
        )

        insight = AutoInsight([df])
        summaries = insight.generate_summary_statistics()

        summary = summaries["Dataset 1"]

        assert summary["missing_values"] is not None
        assert "A" in summary["missing_values"]
        assert summary["missing_values"]["A"] == 1
        assert summary["missing_values"]["B"] == 2

    def test_generate_visualizations_numeric(self, sample_numeric_df):
        """Test visualization generation for numeric data."""
        insight = AutoInsight([sample_numeric_df])
        visualizations = insight.generate_visualizations()

        # Should generate histograms for each numeric column
        assert len(visualizations) >= 3  # At least 3 histograms

        # Check histogram visualization
        hist_viz = [v for v in visualizations if v["type"] == "histogram"]
        assert len(hist_viz) == 3
        assert hist_viz[0]["figure"] is not None
        assert isinstance(hist_viz[0]["figure"], matplotlib.figure.Figure)

    def test_generate_visualizations_categorical(self, sample_categorical_df):
        """Test visualization generation for categorical data."""
        insight = AutoInsight([sample_categorical_df])
        visualizations = insight.generate_visualizations()

        # Should have bar chart for Category
        bar_viz = [v for v in visualizations if v["type"] == "bar"]
        assert len(bar_viz) >= 1

    def test_generate_visualizations_correlation(self, sample_numeric_df):
        """Test correlation heatmap generation."""
        insight = AutoInsight([sample_numeric_df])
        visualizations = insight.generate_visualizations()

        # Should have correlation heatmap
        heatmap_viz = [v for v in visualizations if v["type"] == "heatmap"]
        assert len(heatmap_viz) == 1
        assert heatmap_viz[0]["title"].endswith("Correlation Matrix")

    def test_generate_insights_text(self, sample_mixed_df):
        """Test natural language insights generation."""
        insight = AutoInsight([sample_mixed_df], names=["Employee Data"])
        summaries = insight.generate_summary_statistics()
        text = insight.generate_insights_text(summaries)

        assert "Employee Data" in text
        assert "5 rows" in text
        assert "4 columns" in text
        assert "Numeric Columns" in text or "📈" in text

    def test_generate_full_report(self, sample_mixed_df):
        """Test full report generation."""
        insight = AutoInsight([sample_mixed_df])
        report = insight.generate_full_report()

        assert "insights_text" in report
        assert "visualizations" in report
        assert "summaries" in report

        assert isinstance(report["insights_text"], str)
        assert isinstance(report["visualizations"], list)
        assert isinstance(report["summaries"], dict)

        # Check content
        assert len(report["visualizations"]) > 0
        assert len(report["summaries"]) == 1

    def test_handles_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame()
        insight = AutoInsight([df])

        summaries = insight.generate_summary_statistics()
        visualizations = insight.generate_visualizations()

        assert len(summaries) == 1
        assert summaries["Dataset 1"]["shape"] == (0, 0)
        assert len(visualizations) == 0  # No visualizations for empty df

    def test_multiple_dataframes(self, sample_numeric_df, sample_categorical_df):
        """Test with multiple DataFrames."""
        insight = AutoInsight(
            [sample_numeric_df, sample_categorical_df],
            names=["Numeric Data", "Categorical Data"],
        )

        summaries = insight.generate_summary_statistics()
        visualizations = insight.generate_visualizations()

        assert len(summaries) == 2
        assert "Numeric Data" in summaries
        assert "Categorical Data" in summaries

        # Should have visualizations from both datasets
        assert len(visualizations) > 0

    def test_limits_categorical_columns(self):
        """Test that categorical column analysis is limited."""
        # Create DataFrame with many categorical columns
        df = pd.DataFrame(
            {f"Cat{i}": [f"val{j}" for j in range(10)] for i in range(10)}
        )

        insight = AutoInsight([df])
        summaries = insight.generate_summary_statistics()

        summary = summaries["Dataset 1"]

        # Should only analyze first 5 categorical columns
        assert len(summary["categorical_summary"]) <= 5

    def test_skips_high_cardinality_categorical(self):
        """Test that high cardinality categorical columns are skipped."""
        # Create DataFrame with high cardinality categorical column
        df = pd.DataFrame(
            {
                "HighCardinality": [f"value{i}" for i in range(100)],
                "Value": range(100),
            }
        )

        insight = AutoInsight([df])
        visualizations = insight.generate_visualizations()

        # Should not create bar chart for high cardinality column
        bar_viz = [v for v in visualizations if v["type"] == "bar"]
        assert len(bar_viz) == 0  # High cardinality column skipped

    def test_interestingness_scoring(self):
        """Test that visualizations have interestingness scores."""
        df = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50],
                "Category": ["X", "Y", "X", "Y", "X"],
            }
        )

        insight = AutoInsight([df])
        visualizations = insight.generate_visualizations()

        # All visualizations should have scores
        for viz in visualizations:
            assert "score" in viz
            assert isinstance(viz["score"], (int, float))
            assert viz["score"] >= 0

    def test_visualizations_sorted_by_score(self):
        """Test that full report sorts visualizations by score."""
        df = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50],
                "C": [100, 200, 300, 400, 500],
            }
        )

        insight = AutoInsight([df])
        report = insight.generate_full_report()

        # Check that visualizations are sorted by score (descending)
        scores = [v["score"] for v in report["visualizations"]]
        assert scores == sorted(scores, reverse=True)

    def test_visualizations_organized_by_category(self):
        """Test that visualizations are organized by category."""
        df = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50],
                "Category": ["X", "Y", "X", "Y", "X"],
            }
        )

        insight = AutoInsight([df])
        report = insight.generate_full_report()

        # Check that visualizations_by_category exists
        assert "visualizations_by_category" in report
        viz_by_cat = report["visualizations_by_category"]

        # Check expected categories
        assert "distribution" in viz_by_cat
        assert "correlation" in viz_by_cat
        assert "categorical" in viz_by_cat
        assert "trending" in viz_by_cat

        # Each category should be a list
        for category, viz_list in viz_by_cat.items():
            assert isinstance(viz_list, list)

    def test_trending_analysis_with_dates(self):
        """Test trending analysis for time-series data."""
        dates = pd.date_range("2023-01-01", periods=10, freq="D")
        df = pd.DataFrame({"Date": dates, "Value": range(10, 20)})

        insight = AutoInsight([df])
        visualizations = insight.generate_visualizations()

        # Should create trending visualization
        trend_viz = [v for v in visualizations if v["type"] == "line"]
        assert len(trend_viz) > 0
        assert trend_viz[0]["category"] == "trending"
