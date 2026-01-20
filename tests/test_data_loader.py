"""Unit tests for data loader module."""

import pytest

from src.data_loader import (
    SUPPORTED_EXTENSIONS,
    LoadedData,
    _get_file_extension,
    get_dataframe_info,
    load_excel_files,
    merge_dataframes,
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
        from io import BytesIO

        from openpyxl import Workbook

        wb = Workbook()
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        file_stream.name = "empty.xlsx"

        with pytest.raises(ValueError, match="is empty"):
            load_excel_files([file_stream], validate_empty=True)

    def test_load_non_excel_file(self):
        """Test loading an invalid file type."""
        from io import BytesIO

        invalid_file = BytesIO(b"Some text content")
        invalid_file.name = "test.txt"

        with pytest.raises(
            ValueError, match="(Unsupported file format|Failed to load)"
        ):
            load_excel_files([invalid_file])

    def test_load_excel_with_numeric_column_names(
        self, sample_excel_file_numeric_columns
    ):
        """Test loading Excel file with numeric column names.

        This tests the fix for PandasAI's column_hash error when column names
        are mixed types (strings and integers).
        """
        result = load_excel_files([sample_excel_file_numeric_columns])

        assert len(result) == 1
        # All column names should be converted to strings
        assert all(isinstance(col, str) for col in result[0].data.columns)
        # Verify specific columns exist as strings
        assert "省份" in result[0].data.columns
        assert "20250131" in result[0].data.columns
        assert "20250228" in result[0].data.columns
        assert "20250331" in result[0].data.columns
        # Verify data integrity
        assert len(result[0].data) == 3
        assert result[0].data["省份"].iloc[0] == "北京"

    def test_get_dataframe_info(self):
        """Test getting DataFrame information."""
        import pandas as pd

        df = pd.DataFrame(
            {
                "Name": ["Alice", "Bob", "Charlie"],
                "Sales": [1000, 1500, 1200],
                "Region": ["North", "South", "East"],
            }
        )
        info = get_dataframe_info(df)

        assert info["rows"] == 3
        assert info["columns"] == 3
        assert "Name" in info["column_names"]
        assert "Sales" in info["column_names"]
        assert info["has_nulls"] == False  # noqa: E712

    def test_get_dataframe_info_with_nulls(self):
        """Test getting DataFrame info with null values."""
        import pandas as pd

        df = pd.DataFrame(
            {
                "Name": ["Alice", None, "Charlie"],
                "Sales": [1000, 1500, None],
                "Region": ["North", "South", None],
            }
        )
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

    def test_merge_multiple_dataframes(self, sample_dataframe, sample_excel_file_multi):
        """Test merging multiple DataFrames."""
        import pandas as pd

        from src.data_loader import LoadedData

        df2 = pd.DataFrame(
            {
                "Name": ["Diana", "Eve"],
                "Sales": [800, 1100],
                "Region": ["West", "North"],
            }
        )

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

    def test_load_multiple_csv_files(self, sample_csv_file, sample_csv_file_multi):
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

    def test_mixed_excel_and_csv_files(self, sample_excel_file, sample_csv_file):
        """Test loading both Excel and CSV files together."""
        result = load_excel_files([sample_excel_file, sample_csv_file])

        assert len(result) == 2
        # Excel file
        assert result[0].filename.endswith(".xlsx")
        assert result[0].sheet_name == "Sheet 0"
        # CSV file
        assert result[1].filename.endswith(".csv")
        assert result[1].sheet_name == "CSV"

    def test_load_latin1_csv_file(self):
        """Test loading a CSV file with Latin-1 encoding."""
        from io import BytesIO

        # Create a CSV with Latin-1 encoded character É (0xC9)
        csv_content = b"Product,Quantity,Price,Category\n\xc9lectronics,10,50.0,Electronics\nWidget B,5,75.0,Electronics"
        file_stream = BytesIO(csv_content)
        file_stream.name = "latin1.csv"

        # Should load successfully - encoding detection tries multiple encodings
        # Note: Single-byte ambiguous encodings may decode incorrectly
        # For accurate results, files should be UTF-8 or user should specify encoding
        result = load_excel_files([file_stream])

        assert len(result) == 1
        assert isinstance(result[0], LoadedData)
        assert len(result[0].data) == 2
        assert result[0].filename == "latin1.csv"
        assert result[0].sheet_name == "CSV"

    def test_load_empty_file_list(self):
        """Test loading with empty file list."""
        result = load_excel_files([])
        assert result == []

    def test_load_csv_with_gbk_encoding(self):
        """Test loading a CSV file with GBK encoding (Chinese)."""
        from io import BytesIO

        # Create CSV with GBK encoded Chinese characters
        # "产品" (product) in GBK encoding
        csv_content = b"Product,Quantity\n\xb2\xfa\xc6\xb7,100\n"
        file_stream = BytesIO(csv_content)
        file_stream.name = "gbk.csv"

        result = load_excel_files([file_stream])

        assert len(result) == 1
        assert result[0].data["Product"].iloc[0] == "产品"

    def test_load_csv_with_chinese_filename(self):
        """Test loading a CSV file with Chinese characters in filename."""
        from io import BytesIO

        # Create CSV with Chinese filename
        csv_content = b"Name,Age\nAlice,25\nBob,30\n"
        file_stream = BytesIO(csv_content)
        file_stream.name = "数据分析.csv"  # "Data Analysis" in Chinese

        result = load_excel_files([file_stream])

        assert len(result) == 1
        assert result[0].filename == "数据分析.csv"
        assert len(result[0].data) == 2

    def test_load_csv_with_chinese_column_names(self):
        """Test loading a CSV file with Chinese column names."""
        from io import BytesIO

        # Create CSV with Chinese column names (UTF-8 encoded)
        csv_content = "姓名,年龄,城市\n张三,25,北京\n李四,30,上海\n".encode("utf-8")
        file_stream = BytesIO(csv_content)
        file_stream.name = "chinese_columns.csv"

        result = load_excel_files([file_stream])

        assert len(result) == 1
        assert "姓名" in result[0].data.columns
        assert "年龄" in result[0].data.columns
        assert "城市" in result[0].data.columns
        assert result[0].data["姓名"].iloc[0] == "张三"
        assert result[0].data["城市"].iloc[1] == "上海"

    def test_load_partial_failure_some_files_succeed(self):
        """Test handling when some files load successfully but some fail."""
        from io import BytesIO

        # Create one valid CSV file
        valid_csv = b"Name,Age\nAlice,25\n"
        valid_stream = BytesIO(valid_csv)
        valid_stream.name = "valid.csv"

        # Create one corrupted CSV file (invalid encoding in middle)
        corrupted_csv = b"Name,Age\nAlice,25\nBob,\xff\xfeInvalid\n"
        corrupted_stream = BytesIO(corrupted_csv)
        corrupted_stream.name = "corrupted.csv"

        # Load both - should succeed partially with errors replaced
        result = load_excel_files([valid_stream, corrupted_stream])

        # Valid file should load successfully
        assert len(result) == 2
        assert "valid.csv" in [r.filename for r in result]
        # Corrupted file should load with replacement (we use encoding_errors='replace')
        assert "corrupted.csv" in [r.filename for r in result]

    def test_load_all_files_fail(self):
        """Test handling when all files fail to load."""
        from io import BytesIO

        # Create two invalid files
        file1 = BytesIO(b"invalid,data")
        file1.name = "invalid1.csv"
        file2 = BytesIO(b"also,invalid")
        file2.name = "invalid2.csv"

        # Should raise ValueError (either "empty" or "Failed to load file")
        with pytest.raises(ValueError, match="(empty|Failed to load file)"):
            load_excel_files([file1, file2])

    def test_load_duplicate_filenames(self):
        """Test loading files with duplicate names."""
        from io import BytesIO

        # Create two files with same name
        content1 = b"Name,Age\nAlice,25\n"
        file1 = BytesIO(content1)
        file1.name = "data.csv"

        content2 = b"Name,City\nBob,Paris\n"
        file2 = BytesIO(content2)
        file2.name = "data.csv"

        # Load both - should both succeed
        result = load_excel_files([file1, file2])

        # Both should be loaded
        assert len(result) == 2
        assert all(f.filename == "data.csv" for f in result)

    def test_load_corrupted_file_with_valid_partial(self):
        """Test loading a CSV with encoding issues that can be recovered."""
        from io import BytesIO

        # Create CSV with corrupted bytes in the data (not structural issues)
        # Use a byte sequence that's invalid in UTF-8 but can be replaced
        csv_content = b"Name,Age\nAlice,25\nBob," + b"\xff\xfe" + b"30\n"
        file_stream = BytesIO(csv_content)
        file_stream.name = "partial.csv"

        # Should load with errors replaced (replacement char for invalid bytes)
        result = load_excel_files([file_stream])

        # Should succeed with replacement characters
        assert len(result) == 1
        assert result[0].data["Name"].iloc[0] == "Alice"
        assert result[0].data["Name"].iloc[1] == "Bob"
        # Age column should exist (the replacement char will be there)
        assert "Age" in result[0].data.columns

    def test_load_csv_with_numeric_column_names(self):
        """Test loading CSV with numeric column names (converted to strings)."""
        from io import BytesIO

        # Create CSV with numeric column names (dates)
        csv_content = b"Province,20250131,20250228\nBeijing,100,200\nShanghai,150,250\n"
        file_stream = BytesIO(csv_content)
        file_stream.name = "numeric_cols.csv"

        result = load_excel_files([file_stream])

        assert len(result) == 1
        # All column names should be strings
        assert all(isinstance(col, str) for col in result[0].data.columns)
        assert "Province" in result[0].data.columns
        assert "20250131" in result[0].data.columns
        assert "20250228" in result[0].data.columns


class TestBestEffortLoading:
    """Tests for best-effort file loading."""

    def test_load_excel_files_with_result_all_succeed(self):
        """Test best-effort loading when all files succeed."""
        from io import BytesIO

        from src.data_loader import load_excel_files_with_result

        # Create two valid CSV files
        csv1 = b"Name,Age\nAlice,25\n"
        stream1 = BytesIO(csv1)
        stream1.name = "file1.csv"

        csv2 = b"Product,Price\nApple,1.50\n"
        stream2 = BytesIO(csv2)
        stream2.name = "file2.csv"

        result = load_excel_files_with_result([stream1, stream2])

        assert len(result.successful) == 2
        assert len(result.failed) == 0
        assert "file1.csv" in [r.filename for r in result.successful]
        assert "file2.csv" in [r.filename for r in result.successful]

    def test_load_excel_files_with_result_partial_failure(self):
        """Test best-effort loading when some files fail."""
        from io import BytesIO

        from src.data_loader import load_excel_files_with_result

        # Create one valid CSV file
        valid_csv = b"Name,Age\nAlice,25\n"
        valid_stream = BytesIO(valid_csv)
        valid_stream.name = "valid.csv"

        # Create one invalid file (empty)
        invalid_stream = BytesIO(b"")
        invalid_stream.name = "invalid.csv"

        result = load_excel_files_with_result([valid_stream, invalid_stream])

        assert len(result.successful) == 1
        assert len(result.failed) == 1
        assert "valid.csv" in [r.filename for r in result.successful]
        assert "invalid.csv" in result.failed
        # Check that error message contains relevant info about parsing failure
        assert (
            "empty" in result.failed["invalid.csv"].lower()
            or "columns" in result.failed["invalid.csv"].lower()
        )

    def test_load_excel_files_with_result_all_fail(self):
        """Test best-effort loading when all files fail."""
        from io import BytesIO

        from src.data_loader import load_excel_files_with_result

        # Create two empty files
        stream1 = BytesIO(b"")
        stream1.name = "empty1.csv"

        stream2 = BytesIO(b"")
        stream2.name = "empty2.csv"

        result = load_excel_files_with_result([stream1, stream2])

        assert len(result.successful) == 0
        assert len(result.failed) == 2
        assert "empty1.csv" in result.failed
        assert "empty2.csv" in result.failed

    def test_load_excel_files_best_effort_parameter(self):
        """Test that best_effort parameter works correctly."""
        from io import BytesIO

        # Create one valid and one invalid file
        valid_csv = b"Name,Age\nAlice,25\n"
        valid_stream = BytesIO(valid_csv)
        valid_stream.name = "valid.csv"

        invalid_stream = BytesIO(b"")
        invalid_stream.name = "invalid.csv"

        # With best_effort=True, should return only successful file
        result = load_excel_files([valid_stream, invalid_stream], best_effort=True)

        assert len(result) == 1
        assert result[0].filename == "valid.csv"

    def test_load_excel_files_with_result_unsupported_format(self):
        """Test best-effort loading with unsupported file format."""
        from io import BytesIO

        from src.data_loader import load_excel_files_with_result

        # Create a file with unsupported extension
        stream = BytesIO(b"some content")
        stream.name = "file.txt"

        result = load_excel_files_with_result([stream])

        assert len(result.successful) == 0
        assert len(result.failed) == 1
        assert "file.txt" in result.failed
        assert "Unsupported file format" in result.failed["file.txt"]


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
