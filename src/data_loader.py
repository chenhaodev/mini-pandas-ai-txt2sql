"""Data file loading module for Excel and CSV files."""

import logging
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Union

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


class FileLoadResult(NamedTuple):
    """Represents the result of loading multiple files.

    Attributes:
        successful: List of successfully loaded data files.
        failed: Dict mapping filenames to error messages.
    """

    successful: List[LoadedData]
    failed: Dict[str, str]


def _get_file_extension(filename: str) -> str:
    """Get the lowercase file extension from a filename.

    Args:
        filename: The filename to extract extension from.

    Returns:
        str: The lowercase file extension including the dot.
    """
    return Path(filename).suffix.lower()


def _detect_csv_encoding(file_obj: Any, filename: str) -> str:
    """Detect the encoding of a CSV file by trying multiple encodings.

    For files with some corrupted bytes, tries to find the best-fit encoding
    by testing with error handling, then returns that encoding for use with
    errors='replace' during actual loading.

    Args:
        file_obj: File-like object to read CSV from.
        filename: Name of the file (for error messages).

    Returns:
        str: The detected encoding name.

    Raises:
        ValueError: If no encoding works.
    """
    # Try encodings in order
    # For strict detection: UTF-8 first (most specific), then Asian encodings
    # For error-tolerant detection: Asian encodings first (common for Chinese data),
    # then UTF-8 (which might produce more replacement chars for non-UTF8 Asian text)
    # Separate into strict encodings (multi-byte that can fail) and fallback (single-byte that accept anything)
    strict_encodings_phase1 = ["utf-8-sig", "utf-8"]
    strict_encodings_phase2 = ["gbk", "gb2312"]
    fallback_encodings = ["cp1252", "latin-1"]
    last_error = None

    # First pass: Try strict decoding with UTF-8 variants (most specific)
    for encoding in strict_encodings_phase1:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            pd.read_csv(file_obj, encoding=encoding, encoding_errors="strict", nrows=5)

            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            logger.info(
                f"Successfully detected encoding '{encoding}' for '{filename}' (strict)"
            )
            return encoding

        except (UnicodeDecodeError, LookupError) as e:
            logger.debug(f"Strict decode failed for '{filename}' with {encoding}: {e}")
            last_error = e
            continue
        except Exception:
            raise

    # Try Asian encodings with strict mode
    for encoding in strict_encodings_phase2:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            pd.read_csv(file_obj, encoding=encoding, encoding_errors="strict", nrows=5)

            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            logger.info(
                f"Successfully detected encoding '{encoding}' for '{filename}' (strict)"
            )
            return encoding

        except (UnicodeDecodeError, LookupError) as e:
            logger.debug(f"Strict decode failed for '{filename}' with {encoding}: {e}")
            last_error = e
            continue
        except Exception:
            raise

    # Second pass: For files with corrupted bytes, try Asian encodings FIRST with error handling
    # (Asian encodings are more likely for Chinese filenames like this)
    logger.warning(
        f"No encoding strictly valid for '{filename}', trying with error handling"
    )
    for encoding in strict_encodings_phase2:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            pd.read_csv(file_obj, encoding=encoding, encoding_errors="replace", nrows=5)

            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            logger.warning(
                f"Using encoding '{encoding}' with error replacement for '{filename}'"
            )
            return encoding

        except Exception as e:
            logger.debug(
                f"Failed with error handling for '{filename}' with {encoding}: {e}"
            )
            continue

    # Try UTF-8 with error handling as fallback
    for encoding in strict_encodings_phase1:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            pd.read_csv(file_obj, encoding=encoding, encoding_errors="replace", nrows=5)

            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            logger.warning(
                f"Using encoding '{encoding}' with error replacement for '{filename}'"
            )
            return encoding

        except Exception as e:
            logger.debug(
                f"Failed with error handling for '{filename}' with {encoding}: {e}"
            )
            continue
        except Exception:
            raise

    # Third pass: Fallback to single-byte encodings as last resort
    logger.warning(f"Falling back to single-byte encoding for '{filename}'")
    for encoding in fallback_encodings:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            pd.read_csv(file_obj, encoding=encoding, nrows=5)

            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            logger.warning(f"Using fallback encoding '{encoding}' for '{filename}'")
            return encoding

        except Exception as e:
            logger.debug(f"Fallback failed for '{filename}' with {encoding}: {e}")
            continue

    # No encoding worked at all
    raise ValueError(
        f"Failed to decode CSV file '{filename}' with all tried encodings. "
        f"Last error: {last_error}"
    )


def _get_filename(file_obj: Any) -> str:
    """Extract filename from file object or path.

    Args:
        file_obj: File-like object or file path.

    Returns:
        str: The filename.

    Raises:
        ValueError: If file_obj type is unsupported.
    """
    if hasattr(file_obj, "read"):
        return getattr(file_obj, "name", "unknown")
    elif isinstance(file_obj, (str, Path)):
        return Path(file_obj).name
    else:
        raise ValueError(
            f"Unsupported file type: {type(file_obj).__name__}. "
            "Expected file-like object or path string."
        )


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
    filename = _get_filename(file_obj)

    ext = _get_file_extension(filename)

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{ext}'. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Load based on file type
    if ext in CSV_EXTENSIONS:
        # Detect encoding first
        encoding = _detect_csv_encoding(file_obj, filename)
        logger.info(f"Detected encoding '{encoding}' for CSV file '{filename}'")

        # Load CSV with detected encoding, replace errors for robustness
        df = pd.read_csv(file_obj, encoding=encoding, encoding_errors="replace")
        actual_sheet_name = "CSV"
    else:
        # Excel file
        df = pd.read_excel(file_obj, sheet_name=sheet_name)
        logger.debug(f"Loaded Excel file '{filename}'")
        actual_sheet_name = (
            sheet_name if isinstance(sheet_name, str) else f"Sheet {sheet_name}"
        )

    # Normalize column names to strings (PandasAI requires string column names)
    # Some Excel files may have numeric column names (e.g., dates like 20250131)
    df.columns = df.columns.astype(str)
    logger.debug(f"Normalized column names to strings for '{filename}'")

    # Validate empty DataFrame
    if validate_empty and df.empty:
        raise ValueError(f"File '{filename}' is empty.")

    return [LoadedData(data=df, filename=filename, sheet_name=actual_sheet_name)]


def load_excel_files(
    files: List[Any],
    sheet_name: Union[str, int] = 0,
    validate_empty: bool = True,
    best_effort: bool = False,
) -> List[LoadedData]:
    """Load Excel and CSV files into pandas DataFrames.

    Args:
        files: List of file-like objects or file paths.
        sheet_name: Sheet name or index for Excel files (ignored for CSV).
        validate_empty: Whether to validate that DataFrames are not empty.
        best_effort: If True, continue loading even if some files fail.
                    If False (default), raise on first error.

    Returns:
        List[LoadedData]: List of loaded data with metadata.

    Raises:
        ValueError: If a file is invalid or empty (only when best_effort=False).
    """
    if best_effort:
        result = load_excel_files_with_result(
            files, sheet_name=sheet_name, validate_empty=validate_empty
        )
        return result.successful

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


def load_excel_files_with_result(
    files: List[Any],
    sheet_name: Union[str, int] = 0,
    validate_empty: bool = True,
) -> FileLoadResult:
    """Load Excel and CSV files with best-effort strategy.

    Attempts to load all files, collecting both successes and failures.
    This allows partial data loading even when some files are corrupted.

    Args:
        files: List of file-like objects or file paths.
        sheet_name: Sheet name or index for Excel files (ignored for CSV).
        validate_empty: Whether to validate that DataFrames are not empty.

    Returns:
        FileLoadResult: Object containing successful loads and failure details.
    """
    successful: List[LoadedData] = []
    failed: Dict[str, str] = {}

    for file_obj in files:
        filename = "unknown"
        try:
            filename = _get_filename(file_obj)

            loaded = _load_single_file(
                file_obj,
                sheet_name=sheet_name,
                validate_empty=validate_empty,
            )
            successful.extend(loaded)

            for item in loaded:
                logger.info(
                    f"Loaded {item.filename}: "
                    f"{len(item.data)} rows, {len(item.data.columns)} columns"
                )

        except ValueError as e:
            error_msg = str(e)
            failed[filename] = error_msg
            logger.warning(f"Failed to load file '{filename}': {error_msg}")
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            failed[filename] = error_msg
            logger.warning(f"Failed to load file '{filename}': {error_msg}")

    logger.info(f"Load complete: {len(successful)} successful, {len(failed)} failed")

    return FileLoadResult(successful=successful, failed=failed)


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
