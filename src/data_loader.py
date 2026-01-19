"""Data file loading module for Excel and CSV files."""

import logging
from typing import Any, Dict, List, NamedTuple, Union
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Supported file extensions
EXCEL_EXTENSIONS = {".xlsx", ".xls"}
CSV_EXTENSIONS = {".csv"}
SUPPORTED_EXTENSIONS = EXCEL_EXTENSIONS | CSV_EXTENSIONS


class LoadedData(NamedTuple):
    """Represents a loaded data file with metadata.

    Attributes:
        data: The pandas DataFrame containing the data.
        filename: The original filename.
        sheet_name: The sheet name (for Excel) or 'CSV' for CSV files.
    """

    data: pd.DataFrame
    filename: str
    sheet_name: str


def _get_file_extension(filename: str) -> str:
    """Get the lowercase file extension from a filename.

    Args:
        filename: The filename to extract extension from.

    Returns:
        str: The lowercase file extension including the dot.
    """
    return Path(filename).suffix.lower()


def _load_single_file(
    file_obj: Any,
    sheet_name: Union[str, int] = 0,
    validate_empty: bool = True,
) -> List[LoadedData]:
    """Load a single file (Excel or CSV) into DataFrames.

    Args:
        file_obj: File-like object or file path.
        sheet_name: Sheet name or index for Excel files (ignored for CSV).
        validate_empty: Whether to validate that DataFrames are not empty.

    Returns:
        List[LoadedData]: List of loaded data (may be multiple for Excel sheets).

    Raises:
        ValueError: If the file format is unsupported or file is empty.
    """
    # Determine filename
    if hasattr(file_obj, "read"):
        filename = getattr(file_obj, "name", "unknown")
    elif isinstance(file_obj, (str, Path)):
        filename = Path(file_obj).name
    else:
        raise ValueError(f"Unsupported file type: {type(file_obj)}")

    ext = _get_file_extension(filename)

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{ext}'. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Load based on file type
    if ext in CSV_EXTENSIONS:
        df = pd.read_csv(file_obj)
        actual_sheet_name = "CSV"
    else:
        # Excel file
        df = pd.read_excel(file_obj, sheet_name=sheet_name)
        actual_sheet_name = (
            sheet_name if isinstance(sheet_name, str) else f"Sheet {sheet_name}"
        )

    # Validate empty DataFrame
    if validate_empty and df.empty:
        raise ValueError(f"File '{filename}' is empty.")

    return [LoadedData(data=df, filename=filename, sheet_name=actual_sheet_name)]


def load_excel_files(
    files: List,
    sheet_name: Union[str, int] = 0,
    validate_empty: bool = True,
) -> List[LoadedData]:
    """Load Excel and CSV files into pandas DataFrames.

    Args:
        files: List of file-like objects or file paths.
        sheet_name: Sheet name or index for Excel files (ignored for CSV).
        validate_empty: Whether to validate that DataFrames are not empty.

    Returns:
        List[LoadedData]: List of loaded data with metadata.

    Raises:
        ValueError: If a file is invalid or empty.
    """
    loaded_files: List[LoadedData] = []

    for file_obj in files:
        try:
            loaded = _load_single_file(
                file_obj,
                sheet_name=sheet_name,
                validate_empty=validate_empty,
            )
            loaded_files.extend(loaded)

            for item in loaded:
                logger.info(
                    f"Loaded {item.filename}: "
                    f"{len(item.data)} rows, {len(item.data.columns)} columns"
                )

        except ValueError:
            raise
        except Exception as e:
            filename = getattr(file_obj, "name", "unknown")
            error_msg = f"Failed to load file {filename}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

    return loaded_files


def merge_dataframes(dataframes: List[LoadedData]) -> pd.DataFrame:
    """Merge multiple DataFrames by concatenating them.

    Args:
        dataframes: List of LoadedData objects to merge.

    Returns:
        pd.DataFrame: Merged DataFrame with a source column.

    Raises:
        ValueError: If no DataFrames are provided.
    """
    if not dataframes:
        raise ValueError("No DataFrames to merge")

    # Reason: Add source column to track which file data came from
    dfs_with_source = []
    for loaded_data in dataframes:
        df = loaded_data.data.copy()
        df["_source_file"] = loaded_data.filename
        df["_source_sheet"] = loaded_data.sheet_name
        dfs_with_source.append(df)

    merged = pd.concat(dfs_with_source, ignore_index=True)
    logger.info(f"Merged {len(dataframes)} DataFrames: {len(merged)} total rows")
    return merged


def get_dataframe_info(
    df: "pd.DataFrame",
) -> Dict[str, Any]:
    """Get summary information about a DataFrame.

    Args:
        df: The pandas DataFrame to analyze.

    Returns:
        Dict[str, Any]: Dictionary with DataFrame metadata.
    """
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "memory_usage": df.memory_usage(deep=True).sum(),
        "has_nulls": df.isnull().any().any(),
    }
