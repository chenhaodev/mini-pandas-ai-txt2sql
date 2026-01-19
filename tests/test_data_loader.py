"""Unit tests for data loader module."""

import pytest

from src.data_loader import (
    load_excel_files,
    merge_dataframes,
    get_dataframe_info,
    LoadedData,
)


class TestLoadExcelFiles:
    """Tests for load_excel_files function."""

    def test_load_valid_excel_file(self, sample_excel_file):
        """Test loading a valid Excel file."""
        result = load_excel_files([sample_excel_file])

        assert len(result) == 1
        assert isinstance(result[0], LoadedData)
        assert len(result[0].data) == 4
        assert result[0].filename.endswith((".xlsx", ".xls"))
        assert result[0].sheet_name == "Sheet 0"

    def test_load_multiple_excel_files(
        self, sample_excel_file, sample_excel_file_multi
    ):
        """Test loading multiple Excel files."""
        result = load_excel_files([sample_excel_file, sample_excel_file_multi])

        assert len(result) == 2
        assert len(result[0].data) == 4
        assert len(result[1].data) == 4

    def test_load_empty_excel_file(self):
        """Test loading an Excel file with no data."""
        from openpyxl import Workbook
        from io import BytesIO
        import pandas as pd

        wb = Workbook()
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)

        with pytest.raises(ValueError, match="is empty"):
            load_excel_files([file_stream], validate_empty=True)

    def test_load_non_excel_file(self):
        """Test loading a non-Excel file."""
        from io import BytesIO
        import pandas as pd

        invalid_file = BytesIO(b"not an excel file")
        invalid_file.name = "test.txt"

        with pytest.raises(ValueError, match="(Failed to load|Excel file format)"):
            load_excel_files([invalid_file])

    def test_get_dataframe_info(self):
        """Test getting DataFrame information."""
        import pandas as pd

        df = pd.DataFrame({
            "Name": ["Alice", "Bob", "Charlie"],
            "Sales": [1000, 1500, 1200],
            "Region": ["North", "South", "East"],
        })
        info = get_dataframe_info(df)

        assert info["rows"] == 3
        assert info["columns"] == 3
        assert "Name" in info["column_names"]
        assert "Sales" in info["column_names"]
        assert info["has_nulls"] == False  # noqa: E712

    def test_get_dataframe_info_with_nulls(self):
        """Test getting DataFrame info with null values."""
        import pandas as pd

        df = pd.DataFrame({
            "Name": ["Alice", None, "Charlie"],
            "Sales": [1000, 1500, None],
            "Region": ["North", "South", None],
        })
        info = get_dataframe_info(df)

        assert info["has_nulls"] == True  # noqa: E712


def sample_dataframe_with_nulls():
    """Create a DataFrame with null values for testing."""
    return None  # Not used as fixture, just for inline testing


class TestMergeDataframes:
    """Tests for merge_dataframes function."""

    def test_merge_single_dataframe(self, sample_dataframe):
        """Test merging a single DataFrame."""
        from src.data_loader import LoadedData

        loaded = LoadedData(
            data=sample_dataframe,
            filename="test.xlsx",
            sheet_name="Sheet1",
        )

        result = merge_dataframes([loaded])

        assert len(result) == 3
        assert "_source_file" in result.columns
        assert "_source_sheet" in result.columns
        assert all(result["_source_file"] == "test.xlsx")
        assert all(result["_source_sheet"] == "Sheet1")

    def test_merge_multiple_dataframes(
        self, sample_dataframe, sample_excel_file_multi
    ):
        """Test merging multiple DataFrames."""
        from src.data_loader import LoadedData
        import pandas as pd

        df2 = pd.DataFrame({
            "Name": ["Diana", "Eve"],
            "Sales": [800, 1100],
            "Region": ["West", "North"],
        })

        loaded1 = LoadedData(
            data=sample_dataframe,
            filename="file1.xlsx",
            sheet_name="Sheet1",
        )
        loaded2 = LoadedData(
            data=df2,
            filename="file2.xlsx",
            sheet_name="Sheet2",
        )

        result = merge_dataframes([loaded1, loaded2])

        assert len(result) == 5
        assert set(result["_source_file"].unique()) == {"file1.xlsx", "file2.xlsx"}

    def test_merge_empty_list(self):
        """Test merging empty list of DataFrames."""
        with pytest.raises(ValueError, match="No DataFrames to merge"):
            merge_dataframes([])
