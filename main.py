"""
Retail Data Pipeline - ETL for E-commerce Orders
Spec → Scaffold → Test → Optimize → Deploy
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load order data from CSV file.
    
    Args:
        file_path (str): Path to CSV file
        
    Returns:
        pd.DataFrame: Loaded data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        pd.errors.ParserError: If CSV is malformed
    """
    try:
        logger.info(f"Loading data from {file_path}")
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean dataset: remove duplicates, handle missing values.
    
    Args:
        df (pd.DataFrame): Raw data
        
    Returns:
        pd.DataFrame: Cleaned data
    """
    logger.info("Starting data cleaning")
    
    # Record initial state
    initial_rows = len(df)
    
    # Remove complete duplicates
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    logger.info(f"Removed {duplicates_removed} duplicate rows")
    
    # Handle missing values
    missing_price = df["price"].isna().sum()
    missing_quantity = df["quantity"].isna().sum()
    
    df["quantity"] = df["quantity"].fillna(1)
    df["price"] = df["price"].fillna(0)
    
    logger.info(f"Filled {missing_price} missing prices, {missing_quantity} missing quantities")
    
    # Filter out invalid prices (performance optimization)
    df = df[df["price"] > 0]
    logger.info(f"Filtered out rows with zero/negative prices")
    
    # Ensure data types
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["price"] = pd.to_numeric(df["price"])
    df["quantity"] = pd.to_numeric(df["quantity"])
    
    logger.info(f"Data cleaning complete. Final rows: {len(df)}")
    return df


def transform_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate business metrics: revenue per category and daily sales.
    
    Args:
        df (pd.DataFrame): Cleaned data
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (revenue_by_category, daily_sales)
    """
    logger.info("Starting data transformation")
    
    # Calculate total per order
    df["total"] = df["price"] * df["quantity"]
    
    # Aggregate by category
    revenue_by_category = (
        df.groupby("category")
        .agg({
            "total": "sum",
            "order_id": "count"
        })
        .reset_index()
        .rename(columns={
            "total": "revenue",
            "order_id": "order_count"
        })
        .sort_values("revenue", ascending=False)
    )
    
    logger.info(f"Generated revenue by {len(revenue_by_category)} categories")
    
    # Aggregate by date
    daily_sales = (
        df.groupby("order_date")
        .agg({
            "order_id": "count",
            "total": "sum"
        })
        .reset_index()
        .rename(columns={
            "order_id": "daily_sales_count",
            "total": "daily_revenue"
        })
        .sort_values("order_date")
    )
    
    logger.info(f"Generated daily sales for {len(daily_sales)} days")
    
    return revenue_by_category, daily_sales


def save_data(df: pd.DataFrame, path: str) -> None:
    """
    Save dataframe to CSV file.
    
    Args:
        df (pd.DataFrame): Data to save
        path (str): Output file path
    """
    try:
        logger.info(f"Saving data to {path}")
        df.to_csv(path, index=False)
        logger.info(f"Successfully saved {len(df)} rows to {path}")
    except Exception as e:
        logger.error(f"Error saving data to {path}: {e}")
        raise


def run_pipeline(
    input_file: str = "orders.csv",
    revenue_output: str = "revenue.csv",
    daily_output: str = "daily_sales.csv"
) -> dict:
    """
    Execute complete ETL pipeline.
    
    Args:
        input_file (str): Path to input CSV
        revenue_output (str): Path to revenue output CSV
        daily_output (str): Path to daily sales output CSV
        
    Returns:
        dict: Pipeline execution status and metrics
    """
    pipeline_start = datetime.now()
    logger.info("=" * 60)
    logger.info("RETAIL DATA PIPELINE STARTED")
    logger.info("=" * 60)
    
    try:
        # Load
        df = load_data(input_file)
        initial_rows = len(df)
        
        # Clean
        df = clean_data(df)
        cleaned_rows = len(df)
        
        # Transform
        revenue, daily = transform_data(df)
        
        # Save
        save_data(revenue, revenue_output)
        save_data(daily, daily_output)
        
        pipeline_end = datetime.now()
        duration = (pipeline_end - pipeline_start).total_seconds()
        
        status = {
            "status": "SUCCESS",
            "initial_rows": initial_rows,
            "cleaned_rows": cleaned_rows,
            "rows_removed": initial_rows - cleaned_rows,
            "categories": len(revenue),
            "days": len(daily),
            "total_revenue": revenue["revenue"].sum(),
            "duration_seconds": duration
        }
        
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Rows processed: {initial_rows} → {cleaned_rows}")
        logger.info(f"Categories: {len(revenue)} | Days: {len(daily)}")
        logger.info(f"Total Revenue: ${status['total_revenue']:.2f}")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info("=" * 60)
        
        return status
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("PIPELINE FAILED")
        logger.error(f"Error: {str(e)}")
        logger.error("=" * 60)
        return {
            "status": "FAILED",
            "error": str(e)
        }


if __name__ == "__main__":
    run_pipeline()
