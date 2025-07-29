from typing import Union, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import glob

from canonmap.utils.logger import setup_logger
from canonmap.services.artifact_generation.utils.load_csv import convert_csv_to_df

logger = setup_logger(__name__)

def process_directory(
    dir_path: str,
    recursive: bool = False,
    file_pattern: str = "*.csv",
    num_rows: Optional[int] = None
) -> Dict[str, pd.DataFrame]:
    """
    Process all files in a directory matching the given pattern.
    
    Args:
        dir_path: Directory path to process
        recursive: Whether to search subdirectories
        file_pattern: Glob pattern for file matching
        num_rows: Maximum number of rows to process per file
        
    Returns:
        Dict mapping table names to DataFrames
    """
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        raise ValueError(f"Path {dir_path} is not a directory")

    pattern = "**/" + file_pattern if recursive else file_pattern
    search_path = dir_path / pattern

    files = glob.glob(str(search_path), recursive=recursive)
    if not files:
        raise ValueError(f"No files matching pattern '{file_pattern}' found in {dir_path}")

    dfs = {}
    for file_path in files:
        file_path = Path(file_path)
        table_name = file_path.stem

        try:
            if file_path.suffix.lower() == '.json':
                df = pd.read_json(file_path)
            else:
                df = convert_csv_to_df(str(file_path))

            if num_rows and num_rows < len(df):
                df = df.head(num_rows)

            dfs[table_name] = df
            logger.info(f"Successfully processed {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            continue

    if not dfs:
        raise ValueError("No files were successfully processed")

    return dfs

def convert_data_to_df(
    input_path: Union[str, pd.DataFrame, Dict[str, Any]],
    num_rows: Optional[int] = None,
    recursive: bool = False,
    file_pattern: str = "*.csv",
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Convert various input formats to pandas DataFrames.
    
    Args:
        input_path: Input data (file path, DataFrame, or dict)
        num_rows: Maximum number of rows to process
        recursive: Whether to search subdirectories
        file_pattern: Glob pattern for file matching
        
    Returns:
        DataFrame or dict of DataFrames
    """
    if isinstance(input_path, pd.DataFrame):
        return input_path.head(num_rows) if num_rows and num_rows < len(input_path) else input_path

    elif isinstance(input_path, dict):
        # Check if this is a dict of DataFrames
        if all(isinstance(v, pd.DataFrame) for v in input_path.values()):
            # Return the dict of DataFrames directly
            if num_rows:
                return {k: v.head(num_rows) if num_rows < len(v) else v for k, v in input_path.items()}
            return input_path
        else:
            # Try to create a DataFrame from the dict
            df = pd.DataFrame(input_path)
            return df.head(num_rows) if num_rows and num_rows < len(df) else df

    elif isinstance(input_path, str):
        path = Path(input_path)
        if path.is_dir():
            return process_directory(
                str(path),
                recursive=recursive,
                file_pattern=file_pattern,
                num_rows=num_rows
            )
        else:
            if path.suffix.lower() == '.json':
                df = pd.read_json(input_path)
            else:
                df = convert_csv_to_df(input_path)

            return df.head(num_rows) if num_rows and num_rows < len(df) else df

    raise ValueError(f"Unsupported input type: {type(input_path)}")