"""Unit tests for data loader module."""

import pytest

from src.data_loader import (
    load_excel_files,
    merge_dataframes,
    get_dataframe_info,
    LoadedData,
    SUPPORTED_EXTENSIONS,
    _get_file_extension,
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
        file_stream.name = "empty.xlsx"

        with pytest.raises(ValueError, match="is empty"):
            load_excel_files([file_stream], validate_empty=True)

    def test_load_non_excel_file(self):
        """Test loading a non-Excel file."""
        from io import BytesIO
        import pandas as pd

        invalid_file = BytesIO(b"not an excel file")
        invalid_file.name = "test.txt"

        with pytest.raises(ValueError, match="(Unsupported file format|Failed to load)"):
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


class TestLoadCSVFiles:
    """Tests for CSV file loading functionality."""

    def test_load_valid_csv_file(self, sample_csv_file):
        """Test loading a valid CSV file."""
        result = load_excel_files([sample_csv_file])

        assert len(result) == 1
        assert isinstance(result[0], LoadedData)
        assert len(result[0].data) == 4
        assert result[0].filename.endswith(".csv")
        assert result[0].sheet_name == "CSV"

    def test_load_multiple_csv_files(
        self, sample_csv_file, sample_csv_file_multi
    ):
        """Test loading multiple CSV files."""
        result = load_excel_files([sample_csv_file, sample_csv_file_multi])

        assert len(result) == 2
        assert len(result[0].data) == 4
        assert len(result[1].data) == 4
        assert result[0].sheet_name == "CSV"
        assert result[1].sheet_name == "CSV"

    def test_load_empty_csv_file(self, empty_csv_file):
        """Test loading an empty CSV file."""
        with pytest.raises(ValueError, match="is empty"):
            load_excel_files([empty_csv_file], validate_empty=True)

    def test_load_empty_csv_file_without_validation(self, empty_csv_file):
        """Test loading an empty CSV file without validation."""
        result = load_excel_files([empty_csv_file], validate_empty=False)

        assert len(result) == 1
        assert len(result[0].data) == 0

    def test_csv_data_content(self, sample_csv_file):
        """Test that CSV data is loaded correctly."""
        result = load_excel_files([sample_csv_file])
        df = result[0].data

        assert "Product" in df.columns
        assert "Quantity" in df.columns
        assert "Price" in df.columns
        assert "Category" in df.columns
        assert df["Product"].iloc[0] == "Widget A"
        assert df["Quantity"].iloc[0] == 10

    def test_mixed_excel_and_csv_files(
        self, sample_excel_file, sample_csv_file
    ):
        """Test loading both Excel and CSV files together."""
        result = load_excel_files([sample_excel_file, sample_csv_file])

        assert len(result) == 2
        # Excel file
        assert result[0].filename.endswith(".xlsx")
        assert result[0].sheet_name == "Sheet 0"
        # CSV file
        assert result[1].filename.endswith(".csv")
        assert result[1].sheet_name == "CSV"


class TestFileExtensionHelpers:
    """Tests for file extension helper functions."""

    def test_get_file_extension_xlsx(self):
        """Test extracting xlsx extension."""
        assert _get_file_extension("test.xlsx") == ".xlsx"

    def test_get_file_extension_xls(self):
        """Test extracting xls extension."""
        assert _get_file_extension("test.xls") == ".xls"

    def test_get_file_extension_csv(self):
        """Test extracting csv extension."""
        assert _get_file_extension("test.csv") == ".csv"

    def test_get_file_extension_uppercase(self):
        """Test that extension is lowercased."""
        assert _get_file_extension("test.CSV") == ".csv"
        assert _get_file_extension("test.XLSX") == ".xlsx"

    def test_supported_extensions_contains_expected(self):
        """Test that SUPPORTED_EXTENSIONS contains expected formats."""
        assert ".xlsx" in SUPPORTED_EXTENSIONS
        assert ".xls" in SUPPORTED_EXTENSIONS
        assert ".csv" in SUPPORTED_EXTENSIONS
        assert ".txt" not in SUPPORTED_EXTENSIONS
