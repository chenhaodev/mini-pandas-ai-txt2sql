"""Excel file loading module."""

import logging
from typing import Any, Dict, List, NamedTuple
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class LoadedData(NamedTuple):
    """Represents a loaded Excel file with metadata.

    Attributes:
        data: The pandas DataFrame containing the data.
        filename: The original filename.
        sheet_name: The sheet name from the Excel file.
    """

    data: pd.DataFrame
    filename: str
    sheet_name: str


def load_excel_files(  # noqa: ruff
    files: List,
    sheet_name: str = 0,
    validate_empty: bool = True,
) -> List[LoadedData]:  # noqa: ruff
    """Load Excel files into pandas DataFrames.

    Args:
        files: List of file-like objects or file paths to Excel files.
        sheet_name: Sheet name or index to load (default: 0 for first sheet).
        validate_empty: Whether to validate that DataFrames are not empty.

    Returns:
        List[LoadedData]: List of loaded data with metadata.

    Raises:
        ValueError: If a file is not a valid Excel file or is empty.
    """
    loaded_files: List[LoadedData] = []

    for file_obj in files:
        try:
            # Handle both file-like objects and file paths
            if hasattr(file_obj, "read"):
                # File-like object from Streamlit
                filename = getattr(file_obj, "name", "unknown.xlsx")
                df = pd.read_excel(file_obj, sheet_name=sheet_name)
            elif isinstance(file_obj, (str, Path)):
                # File path
                filename = Path(file_obj).name
                df = pd.read_excel(file_obj, sheet_name=sheet_name)
            else:
                raise ValueError(f"Unsupported file type: {type(file_obj)}")

            # Get actual sheet name if index was used
            actual_sheet_name = (
                sheet_name if isinstance(sheet_name, str) else f"Sheet {sheet_name}"
            )

            # Validate empty DataFrame
            if validate_empty and df.empty:
                raise ValueError(
                    f"File '{filename}' sheet '{actual_sheet_name}' is empty."
                )

            loaded = LoadedData(
                data=df,
                filename=filename,
                sheet_name=actual_sheet_name,
            )
            loaded_files.append(loaded)
            logger.info(
                f"Loaded {filename}: {len(df)} rows, {len(df.columns)} columns"
            )

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Reason: Provide user-friendly error for invalid files
            error_msg = f"Failed to load file {getattr(file_obj, 'name', 'unknown')}: {e}"
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
