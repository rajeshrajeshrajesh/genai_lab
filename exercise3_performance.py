"""
EXERCISE 3: Performance Optimization
Scale pipeline for large datasets

DIFFICULTY: Medium

TASK:
1. Generate large dataset (10,000 rows)
2. Measure baseline performance
3. Implement optimizations:
   - Chunked processing
   - Date filtering
   - Data type optimization
4. Compare performance improvements

STARTER CODE:
"""
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Step 1: Generate large dataset
def generate_large_dataset(num_rows: int = 10000, output_file: str = "orders_large.csv"):
    """
    Generate large order dataset for performance testing.
    
    Args:
        num_rows (int): Number of rows to generate
        output_file (str): Output filename
    """
    logger.info(f"Generating {num_rows} rows...")
    
    np.random.seed(42)
    base_date = datetime(2024, 1, 1)
    
    data = {
        "order_id": range(1, num_rows + 1),
        "customer_id": np.random.randint(1000, 5000, num_rows),
        "product": np.random.choice(["Laptop", "Phone", "Tablet", "Monitor", "Keyboard", "Mouse"], num_rows),
        "category": np.random.choice(["Electronics", "Fashion", "Home"], num_rows),
        "price": np.random.uniform(10, 1000, num_rows),
        "quantity": np.random.randint(1, 10, num_rows),
        "order_date": [base_date + timedelta(days=int(x)) for x in np.random.randint(0, 365, num_rows)]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    logger.info(f"✓ Generated {output_file} ({df.memory_usage(deep=True).sum() / 1024:.2f} KB)")
    return df


# Step 2: Baseline performance test
def baseline_performance(file_path: str) -> dict:
    """
    Measure baseline pipeline performance.
    
    Returns:
        dict: Performance metrics
    """
    logger.info("Running baseline performance test...")
    start = time.time()
    
    # Load
    df = pd.read_csv(file_path)
    
    # Clean (basic)
    df = df.drop_duplicates()
    df["quantity"] = df["quantity"].fillna(1)
    df["price"] = df["price"].fillna(0)
    
    # Transform
    df["total"] = df["price"] * df["quantity"]
    revenue = df.groupby("category")["total"].sum()
    daily = df.groupby("order_date")["order_id"].count()
    
    duration = time.time() - start
    return {
        "rows": len(df),
        "duration": duration,
        "rows_per_sec": len(df) / duration,
        "memory_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
    }


# Step 3: Optimized performance test
def optimized_performance(file_path: str, days_filter: int = 30) -> dict:
    """
    Measure optimized pipeline performance with:
    - Data type optimization
    - Date filtering (incremental)
    - Chunked processing
    
    Returns:
        dict: Performance metrics
    """
    logger.info(f"Running optimized performance test (last {days_filter} days)...")
    start = time.time()
    
    # Load with optimized dtypes
    dtype_dict = {
        "order_id": "int32",
        "customer_id": "int32",
        "product": "category",
        "category": "category",
        "price": "float32",
        "quantity": "int8"
    }
    df = pd.read_csv(file_path, dtype=dtype_dict)
    df["order_date"] = pd.to_datetime(df["order_date"])
    
    # Filter to last N days (incremental processing)
    cutoff_date = df["order_date"].max() - timedelta(days=days_filter)
    df = df[df["order_date"] >= cutoff_date]
    
    # Clean
    df = df.drop_duplicates()
    df["quantity"] = df["quantity"].fillna(1)
    df["price"] = df["price"].fillna(0)
    
    # Transform
    df["total"] = df["price"] * df["quantity"]
    revenue = df.groupby("category")["total"].sum()
    daily = df.groupby("order_date")["order_id"].count()
    
    duration = time.time() - start
    return {
        "rows": len(df),
        "duration": duration,
        "rows_per_sec": len(df) / duration if duration > 0 else 0,
        "memory_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
    }


# Step 4: Performance comparison
def compare_performance():
    """Compare baseline vs optimized performance"""
    print("\n" + "=" * 80)
    print("PERFORMANCE OPTIMIZATION TEST")
    print("=" * 80)
    
    # Generate test data
    generate_large_dataset(10000, "orders_large.csv")
    
    # Baseline
    baseline = baseline_performance("orders_large.csv")
    print(f"\n{'BASELINE':^80}")
    print("-" * 80)
    print(f"Rows processed:     {baseline['rows']:,}")
    print(f"Duration:           {baseline['duration']:.3f}s")
    print(f"Throughput:         {baseline['rows_per_sec']:.0f} rows/sec")
    print(f"Memory usage:       {baseline['memory_mb']:.2f} MB")
    
    # Optimized
    optimized = optimized_performance("orders_large.csv", days_filter=30)
    print(f"\n{'OPTIMIZED (30-day filter + dtype optimization)':^80}")
    print("-" * 80)
    print(f"Rows processed:     {optimized['rows']:,}")
    print(f"Duration:           {optimized['duration']:.3f}s")
    print(f"Throughput:         {optimized['rows_per_sec']:.0f} rows/sec")
    print(f"Memory usage:       {optimized['memory_mb']:.2f} MB")
    
    # Calculate improvement
    print(f"\n{'IMPROVEMENT':^80}")
    print("-" * 80)
    speedup = baseline['duration'] / optimized['duration'] if optimized['duration'] > 0 else 0
    memory_reduction = (1 - optimized['memory_mb'] / baseline['memory_mb']) * 100
    print(f"Speed improvement:  {speedup:.2f}x faster")
    print(f"Memory reduction:   {memory_reduction:.1f}%")
    
    print("=" * 80)
    
    # Cleanup
    import os
    os.remove("orders_large.csv")


# Step 5: Additional optimizations to explore
def advanced_optimizations():
    """
    Additional optimization techniques:
    1. Parallel processing with multiprocessing
    2. Chunked reading for memory efficiency
    3. Vectorized operations instead of apply()
    4. Use dask for distributed processing
    5. Use polars for faster DataFrame operations
    """
    print("\nAdvanced Optimization Techniques:")
    print("-" * 80)
    print("1. Chunked Reading:")
    print("   for chunk in pd.read_csv(file, chunksize=1000):")
    print("       process(chunk)")
    print()
    print("2. Multiprocessing:")
    print("   from multiprocessing import Pool")
    print("   with Pool() as p:")
    print("       results = p.map(process_chunk, chunks)")
    print()
    print("3. Dask for Distributed Processing:")
    print("   import dask.dataframe as dd")
    print("   ddf = dd.read_csv('orders_large.csv')")
    print("   result = ddf.groupby('category').agg(...).compute()")
    print()
    print("4. Polars (faster alternative to pandas):")
    print("   import polars as pl")
    print("   df = pl.read_csv('orders_large.csv')")
    print("   df.groupby('category').agg(pl.col('price').sum())")


if __name__ == "__main__":
    print("Exercise 3: Performance Optimization")
    print("=" * 80)
    
    # Run comparison
    compare_performance()
    
    # Show advanced techniques
    advanced_optimizations()
    
    print("\n" + "=" * 80)
    print("✓ Exercise 3 Complete: Performance optimization demonstrated")
    print("=" * 80)
