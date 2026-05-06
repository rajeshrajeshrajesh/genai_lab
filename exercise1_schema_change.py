"""
EXERCISE 1: Schema Change
Add a 'discount' column to the pipeline

DIFFICULTY: Easy

TASK:
1. Add discount column to orders.csv
2. Update transform_data() to calculate net_revenue
3. Add tests for discount handling
4. Run full pipeline

STARTER CODE:
"""

import pandas as pd
from main import load_data, clean_data, save_data

# TODO: Step 1 - Load data with new discount column
# df = load_data("orders_with_discount.csv")

# TODO: Step 2 - Implement clean_data() call
# df_clean = clean_data(df)

# TODO: Step 3 - Create transform_data_with_discount function
def transform_data_with_discount(df: pd.DataFrame):
    """
    Generate business metrics with discount calculations.
    
    Args:
        df (pd.DataFrame): Cleaned data with discount column
        
    Returns:
        Tuple of revenue aggregations with discount applied
    """
    # Calculate gross total
    df["gross_total"] = df["price"] * df["quantity"]
    
    # TODO: Calculate net total with discount
    # df["net_total"] = df["gross_total"] * (1 - df["discount"])
    
    # Revenue by category (with discount)
    # revenue_by_category = df.groupby("category").agg({...})
    
    # Return aggregations
    # return revenue_by_category, daily_sales


# TODO: Step 4 - Save results
# save_data(revenue, "revenue_with_discount.csv")
# save_data(daily, "daily_sales_with_discount.csv")


if __name__ == "__main__":
    print("Exercise 1: Schema Change - Add Discount Column")
    print("=" * 60)
    print("✓ Create orders_with_discount.csv with discount column")
    print("✓ Implement transform_data_with_discount()")
    print("✓ Calculate net_revenue = gross_total * (1 - discount)")
    print("✓ Verify revenue calculations")
    print("=" * 60)
    
    # TODO: Call your implementation here
    # transform_data_with_discount(df_clean)
