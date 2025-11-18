"""
Data import service - adapted from arauto/lib/file_selector.py
"""
import os
import pandas as pd
from typing import Tuple, Dict, Any
from pathlib import Path


class DataImportService:
    """Service for importing and parsing data files"""

    @staticmethod
    def parse_file(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parse a data file (CSV, Excel) with automatic encoding/delimiter detection
        
        Adapted from arauto/lib/file_selector.py
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Tuple of (DataFrame, metadata dict)
            
        Raises:
            ValueError: If file format is not supported or parsing fails
        """
        file_ext = Path(file_path).suffix.lower()
        metadata = {
            "filename": os.path.basename(file_path),
            "file_path": file_path,
            "file_extension": file_ext,
        }
        
        df = None
        
        # Handle CSV/TXT files
        if file_ext in ['.csv', '.txt']:
            df = DataImportService._parse_csv(file_path)
            
        # Handle Excel files
        elif file_ext in ['.xls', '.xlsx']:
            df = DataImportService._parse_excel(file_path)
        else:
            raise ValueError(f"File format {file_ext} is not supported. Supported formats: CSV, TXT, XLS, XLSX")
        
        # Validate data
        if len(df) < 30:
            metadata["warning"] = (
                "The dataset contains too few data points to make a prediction. "
                "It is recommended to have at least 50 data points, but preferably 100 data points. "
                "This may lead to inaccurate predictions."
            )
        
        metadata.update({
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
        })
        
        return df, metadata
    
    @staticmethod
    def _parse_csv(file_path: str) -> pd.DataFrame:
        """Parse CSV file with automatic encoding/delimiter detection"""
        # Try default CSV parsing
        try:
            return pd.read_csv(file_path)
        except pd.errors.ParserError:
            # Try semicolon delimiter
            try:
                return pd.read_csv(file_path, delimiter=';')
            except UnicodeDecodeError:
                return pd.read_csv(file_path, delimiter=';', encoding='latin1')
        except UnicodeDecodeError:
            # Try latin1 encoding
            try:
                return pd.read_csv(file_path, encoding='latin1')
            except pd.errors.ParserError:
                return pd.read_csv(file_path, encoding='latin1', delimiter=';')
    
    @staticmethod
    def _parse_excel(file_path: str) -> pd.DataFrame:
        """Parse Excel file with automatic encoding detection"""
        try:
            return pd.read_excel(file_path)
        except Exception:
            # Try with latin1 encoding if needed
            try:
                return pd.read_excel(file_path, encoding='latin1')
            except Exception:
                raise ValueError(f"Failed to parse Excel file: {file_path}")
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate dataframe and return validation results
        
        Returns:
            Dict with validation results and warnings
        """
        validation = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
        }
        
        # Check minimum data points
        if len(df) < 30:
            validation["warnings"].append(
                "Dataset contains fewer than 30 data points. "
                "At least 50 data points are recommended for accurate predictions."
            )
        
        # Check for missing values
        missing_counts = df.isnull().sum()
        if missing_counts.any():
            cols_with_missing = missing_counts[missing_counts > 0].to_dict()
            validation["warnings"].append(
                f"Found missing values in columns: {list(cols_with_missing.keys())}"
            )
        
        # Check for empty dataframe
        if df.empty:
            validation["is_valid"] = False
            validation["errors"].append("DataFrame is empty")
        
        return validation

