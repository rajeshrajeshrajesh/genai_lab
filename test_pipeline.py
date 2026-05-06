"""
Test Suite for Retail Data Pipeline
Tests validation, error handling, and output correctness
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from main import (
    load_data,
    clean_data,
    transform_data,
    save_data,
    run_pipeline
)


class TestLoadData:
    """Tests for load_data function"""
    
    def test_orders_file_exists_and_loads(self):
        """Verify orders.csv exists and can be loaded"""
        df = load_data("orders.csv")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_required_columns_present(self):
        """Verify all required columns exist"""
        df = load_data("orders.csv")
        required_cols = ["order_id", "customer_id", "product", "category", 
                        "price", "quantity", "order_date"]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_nonexistent_file_raises_error(self):
        """Verify FileNotFoundError for missing file"""
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent.csv")
    
    def test_correct_data_types(self):
        """Verify data types after loading"""
        df = load_data("orders.csv")
        assert pd.api.types.is_numeric_dtype(df["order_id"])
        assert pd.api.types.is_numeric_dtype(df["customer_id"])
        assert pd.api.types.is_numeric_dtype(df["price"])


class TestCleanData:
    """Tests for clean_data function"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return pd.DataFrame({
            "order_id": [1, 2, 2, 3, 4],
            "customer_id": [101, 102, 102, 103, 104],
            "product": ["A", "B", "B", "C", "D"],
            "category": ["X", "Y", "Y", "Z", "X"],
            "price": [100, 200, 200, np.nan, 50],
            "quantity": [1, 2, 2, 1, np.nan],
            "order_date": ["2024-01-01", "2024-01-01", "2024-01-01", 
                          "2024-01-02", "2024-01-02"]
        })
    
    def test_duplicates_removed(self, sample_data):
        """Verify duplicates are removed"""
        initial_rows = len(sample_data)
        cleaned = clean_data(sample_data)
        assert len(cleaned) < initial_rows
        assert not cleaned.duplicated(subset=["order_id", "customer_id", "price"]).any()
    
    def test_no_null_prices_after_cleaning(self, sample_data):
        """Verify no null values in price after cleaning"""
        cleaned = clean_data(sample_data)
        assert cleaned["price"].isna().sum() == 0
    
    def test_no_null_quantities_after_cleaning(self, sample_data):
        """Verify no null values in quantity after cleaning"""
        cleaned = clean_data(sample_data)
        assert cleaned["quantity"].isna().sum() == 0
    
    def test_missing_quantities_filled_with_one(self, sample_data):
        """Verify missing quantities default to 1"""
        cleaned = clean_data(sample_data)
        # All quantities should be >= 1
        assert (cleaned["quantity"] >= 1).all()
    
    def test_zero_price_rows_removed(self, sample_data):
        """Verify rows with zero/negative prices are filtered"""
        cleaned = clean_data(sample_data)
        assert (cleaned["price"] > 0).all()
    
    def test_order_date_converted_to_datetime(self):
        """Verify order_date is converted to datetime"""
        df = load_data("orders.csv")
        cleaned = clean_data(df)
        assert pd.api.types.is_datetime64_any_dtype(cleaned["order_date"])


class TestTransformData:
    """Tests for transform_data function"""
    
    def test_revenue_by_category_calculated(self):
        """Verify revenue aggregation by category"""
        df = load_data("orders.csv")
        df = clean_data(df)
        revenue, _ = transform_data(df)
        
        assert isinstance(revenue, pd.DataFrame)
        assert len(revenue) > 0
        assert "category" in revenue.columns
        assert "revenue" in revenue.columns
    
    def test_daily_sales_calculated(self):
        """Verify daily sales aggregation"""
        df = load_data("orders.csv")
        df = clean_data(df)
        _, daily = transform_data(df)
        
        assert isinstance(daily, pd.DataFrame)
        assert len(daily) > 0
        assert "order_date" in daily.columns
        assert "daily_sales_count" in daily.columns
        assert "daily_revenue" in daily.columns
    
    def test_revenue_totals_match(self):
        """Verify revenue totals are calculated correctly"""
        df = load_data("orders.csv")
        df = clean_data(df)
        revenue, daily = transform_data(df)
        
        total_revenue_cat = revenue["revenue"].sum()
        total_revenue_daily = daily["daily_revenue"].sum()
        
        # Should be approximately equal (floating point tolerance)
        assert abs(total_revenue_cat - total_revenue_daily) < 0.01
    
    def test_no_negative_revenue(self):
        """Verify no negative revenue values"""
        df = load_data("orders.csv")
        df = clean_data(df)
        revenue, daily = transform_data(df)
        
        assert (revenue["revenue"] >= 0).all()
        assert (daily["daily_revenue"] >= 0).all()
    
    def test_revenue_sorted_descending(self):
        """Verify revenue by category is sorted"""
        df = load_data("orders.csv")
        df = clean_data(df)
        revenue, _ = transform_data(df)
        
        # Check if sorted in descending order
        assert (revenue["revenue"].values == sorted(revenue["revenue"].values, reverse=True)).all()


class TestSaveData:
    """Tests for save_data function"""
    
    def test_save_data_creates_file(self):
        """Verify save_data creates output file"""
        test_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        output_path = "test_output.csv"
        
        save_data(test_df, output_path)
        
        assert Path(output_path).exists()
        # Cleanup
        Path(output_path).unlink()
    
    def test_saved_data_readable(self):
        """Verify saved data can be read back"""
        test_df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        output_path = "test_output.csv"
        
        save_data(test_df, output_path)
        loaded_df = pd.read_csv(output_path)
        
        assert len(loaded_df) == len(test_df)
        assert list(loaded_df.columns) == list(test_df.columns)
        
        # Cleanup
        Path(output_path).unlink()


class TestPipelineIntegration:
    """End-to-end pipeline tests"""
    
    def test_full_pipeline_runs_successfully(self):
        """Verify complete pipeline executes without errors"""
        result = run_pipeline(
            input_file="orders.csv",
            revenue_output="test_revenue.csv",
            daily_output="test_daily.csv"
        )
        
        assert result["status"] == "SUCCESS"
        assert "initial_rows" in result
        assert "cleaned_rows" in result
        assert "total_revenue" in result
        
        # Cleanup
        Path("test_revenue.csv").unlink(missing_ok=True)
        Path("test_daily.csv").unlink(missing_ok=True)
    
    def test_pipeline_outputs_exist(self):
        """Verify pipeline creates output files"""
        run_pipeline(
            input_file="orders.csv",
            revenue_output="test_revenue.csv",
            daily_output="test_daily.csv"
        )
        
        assert Path("test_revenue.csv").exists()
        assert Path("test_daily.csv").exists()
        
        # Cleanup
        Path("test_revenue.csv").unlink()
        Path("test_daily.csv").unlink()
    
    def test_pipeline_metrics_valid(self):
        """Verify pipeline metrics are reasonable"""
        result = run_pipeline(
            input_file="orders.csv",
            revenue_output="test_revenue.csv",
            daily_output="test_daily.csv"
        )
        
        assert result["cleaned_rows"] > 0
        assert result["total_revenue"] > 0
        assert result["duration_seconds"] >= 0
        assert result["categories"] > 0
        assert result["days"] > 0
        
        # Cleanup
        Path("test_revenue.csv").unlink(missing_ok=True)
        Path("test_daily.csv").unlink(missing_ok=True)
    
    def test_rows_removed_is_reasonable(self):
        """Verify rows removed count is logical"""
        result = run_pipeline(
            input_file="orders.csv",
            revenue_output="test_revenue.csv",
            daily_output="test_daily.csv"
        )
        
        # Rows removed should not exceed initial rows
        assert result["rows_removed"] <= result["initial_rows"]
        # Cleaned rows should be positive
        assert result["cleaned_rows"] > 0
        
        # Cleanup
        Path("test_revenue.csv").unlink(missing_ok=True)
        Path("test_daily.csv").unlink(missing_ok=True)


class TestErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_empty_dataframe_handling(self):
        """Verify pipeline handles empty data gracefully"""
        empty_df = pd.DataFrame({
            "order_id": [],
            "customer_id": [],
            "product": [],
            "category": [],
            "price": [],
            "quantity": [],
            "order_date": []
        })
        
        # Should not raise an error
        cleaned = clean_data(empty_df)
        assert isinstance(cleaned, pd.DataFrame)
    
    def test_malformed_csv_handling(self):
        """Verify error is raised for malformed CSV"""
        # Create temporary malformed CSV
        with open("malformed.csv", "w") as f:
            f.write("col1,col2,col3\n1,2\n")  # Missing value in row
        
        try:
            with pytest.raises(Exception):
                load_data("malformed.csv")
        finally:
            Path("malformed.csv").unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
