"""
EXERCISE 2: Bug Simulation & Debugging
Detect and fix pipeline errors

DIFFICULTY: Medium

TASK:
1. Create orders_broken.csv without 'price' column
2. Run pipeline and observe error
3. Fix error handling in load_data()
4. Create test case for missing column
5. Verify pipeline gracefully handles error

INSTRUCTIONS:
"""
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Step 1: Create broken CSV file
def create_broken_dataset():
    """Create CSV missing required columns"""
    broken_df = pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5],
        "customer_id": [101, 102, 103, 104, 105],
        "product": ["A", "B", "C", "D", "E"],
        "category": ["X", "Y", "Z", "X", "Y"],
        # Missing 'price' column - THIS IS THE BUG!
        "quantity": [1, 2, 1, 3, 2],
        "order_date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    })
    broken_df.to_csv("orders_broken.csv", index=False)
    logger.info("Created orders_broken.csv (missing price column)")


# Step 2: Enhanced error handling
def load_data_robust(file_path: str, required_columns: list) -> pd.DataFrame:
    """
    Load data with validation for required columns.
    
    Args:
        file_path (str): Path to CSV
        required_columns (list): Required column names
        
    Returns:
        pd.DataFrame: Validated data or None if errors
    """
    try:
        logger.info(f"Loading {file_path}...")
        df = pd.read_csv(file_path)
        
        # TODO: Check for missing columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            logger.error(f"Available columns: {list(df.columns)}")
            raise ValueError(f"Missing columns: {missing_cols}")
        
        logger.info(f"✓ All required columns present")
        return df
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {file_path}")
        return None
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


# Step 3: Test case for missing column
def test_missing_column_handling():
    """Test pipeline behavior with missing column"""
    print("\n" + "=" * 60)
    print("TEST: Missing Column Handling")
    print("=" * 60)
    
    required_cols = ["order_id", "customer_id", "product", "category", "price", "quantity", "order_date"]
    
    df = load_data_robust("orders_broken.csv", required_cols)
    
    if df is None:
        print("✓ Pipeline correctly detected and reported error")
        return True
    else:
        print("✗ Pipeline failed to detect missing column")
        return False


# Step 4: Compare error handling
def demonstrate_error_handling():
    """Show before/after error handling"""
    print("\n" + "=" * 60)
    print("ERROR HANDLING COMPARISON")
    print("=" * 60)
    
    print("\n❌ WITHOUT proper error handling:")
    print("   KeyError: 'price' not in index")
    print("   (Stack trace - not helpful)")
    
    print("\n✅ WITH proper error handling:")
    print("   ValueError: Missing columns: ['price']")
    print("   Available columns: ['order_id', 'customer_id', ...]")
    print("   (Clear, actionable error message)")


if __name__ == "__main__":
    print("Exercise 2: Bug Simulation & Debugging")
    print("=" * 60)
    
    # Step 1: Create broken CSV
    create_broken_dataset()
    
    # Step 2: Show error handling comparison
    demonstrate_error_handling()
    
    # Step 3: Test the robust loader
    success = test_missing_column_handling()
    
    # Step 4: Cleanup
    Path("orders_broken.csv").unlink(missing_ok=True)
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Exercise 2 Complete: Error handling works correctly")
    else:
        print("✗ Exercise 2 Failed: Need better error handling")
    print("=" * 60)
