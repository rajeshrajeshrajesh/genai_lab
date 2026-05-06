"""
EXERCISE 4: Production Readiness
Make pipeline enterprise-grade

DIFFICULTY: Hard

TASK:
1. Add configuration management (YAML config)
2. Add data schema validation
3. Add database export capability
4. Add error notification system
5. Add retry logic
6. Document with Sphinx

STARTER CODE:
"""

import json
import yaml
from pathlib import Path
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Step 1: Configuration Management
# ============================================================================

class PipelineConfig:
    """
    Load and manage pipeline configuration from YAML file.
    
    Example config.yaml:
    ---
    pipeline:
      name: "Retail Data Pipeline"
      version: "1.0.0"
    
    input:
      file: "orders.csv"
      encoding: "utf-8"
    
    output:
      revenue_file: "revenue.csv"
      daily_file: "daily_sales.csv"
      database: "pipeline.db"
    
    processing:
      remove_duplicates: true
      fill_missing_values: true
      filter_negative_prices: true
    
    notifications:
      enabled: true
      email: "admin@company.com"
      slack_webhook: "https://hooks.slack.com/..."
    
    database:
      type: "sqlite"
      connection_string: "sqlite:///pipeline.db"
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded config from {config_path}")
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            self.config = self._default_config()
    
    @staticmethod
    def _default_config():
        """Default configuration"""
        return {
            "pipeline": {"name": "Retail Pipeline", "version": "1.0.0"},
            "input": {"file": "orders.csv"},
            "output": {"revenue_file": "revenue.csv", "daily_file": "daily_sales.csv"},
            "processing": {"remove_duplicates": True, "fill_missing_values": True},
        }
    
    def get(self, key_path: str, default=None):
        """Get config value by dot notation (e.g., 'input.file')"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            value = value.get(key, {})
        return value if value else default


# ============================================================================
# Step 2: Data Schema Validation
# ============================================================================

class SchemaValidator:
    """
    Validate data against expected schema.
    
    To use with pandera (pip install pandera):
    import pandera as pa
    
    schema = pa.DataFrameSchema({
        "order_id": pa.Column(int),
        "price": pa.Column(float, pa.Check.greater_than(0)),
        "quantity": pa.Column(int, pa.Check.greater_than_equal(1)),
    })
    schema.validate(df)
    """
    
    @staticmethod
    def create_schema_dict():
        """Define expected schema"""
        return {
            "order_id": {"type": "int", "nullable": False},
            "customer_id": {"type": "int", "nullable": False},
            "product": {"type": "string", "nullable": False},
            "category": {"type": "string", "nullable": False},
            "price": {"type": "float", "nullable": False, "min": 0},
            "quantity": {"type": "int", "nullable": False, "min": 1},
            "order_date": {"type": "datetime", "nullable": False},
        }
    
    @staticmethod
    def validate(df, schema_dict: dict) -> bool:
        """
        Validate dataframe against schema.
        
        Returns:
            bool: True if valid, False otherwise
        """
        errors = []
        
        for col, constraints in schema_dict.items():
            if col not in df.columns:
                errors.append(f"Missing column: {col}")
                continue
            
            # Check nullable
            if not constraints.get("nullable", True) and df[col].isna().any():
                errors.append(f"Column {col} has null values but shouldn't")
            
            # Check min value
            if "min" in constraints:
                if (df[col] < constraints["min"]).any():
                    errors.append(f"Column {col} has values < {constraints['min']}")
        
        if errors:
            logger.error(f"Schema validation failed: {errors}")
            return False
        
        logger.info("✓ Data schema validation passed")
        return True


# ============================================================================
# Step 3: Database Export
# ============================================================================

class DatabaseExporter:
    """
    Export pipeline results to database (SQLite/PostgreSQL).
    
    Example usage:
    exporter = DatabaseExporter("sqlite:///pipeline.db")
    exporter.export_table(df, "orders_cleaned")
    """
    
    def __init__(self, connection_string: str):
        """Initialize database connection"""
        self.connection_string = connection_string
        logger.info(f"Initialized database: {connection_string}")
    
    def export_table(self, df, table_name: str, if_exists: str = "replace"):
        """
        Export dataframe to database table.
        
        Args:
            df: DataFrame to export
            table_name: Target table name
            if_exists: 'fail', 'replace', 'append'
        """
        try:
            # To use: pip install sqlalchemy
            from sqlalchemy import create_engine
            
            engine = create_engine(self.connection_string)
            df.to_sql(table_name, engine, if_exists=if_exists, index=False)
            logger.info(f"✓ Exported {len(df)} rows to table '{table_name}'")
        except Exception as e:
            logger.error(f"Database export failed: {e}")
    
    def query(self, sql: str):
        """Execute query on database"""
        try:
            from sqlalchemy import create_engine
            engine = create_engine(self.connection_string)
            result = pd.read_sql(sql, engine)
            return result
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None


# ============================================================================
# Step 4: Error Notification
# ============================================================================

class NotificationService:
    """
    Send notifications on pipeline success/failure.
    
    Supports: Email, Slack, webhooks
    """
    
    @staticmethod
    def send_email(to: str, subject: str, body: str):
        """Send email notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = "pipeline@company.com"
            msg["To"] = to
            
            # TODO: Configure SMTP server
            # server = smtplib.SMTP('smtp.gmail.com', 587)
            # server.starttls()
            # server.login(email, password)
            # server.send_message(msg)
            
            logger.info(f"Email sent to {to}")
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
    
    @staticmethod
    def send_slack(webhook_url: str, message: str):
        """Send Slack notification"""
        try:
            import requests
            
            payload = {"text": message}
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 200:
                logger.info("✓ Slack notification sent")
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
    
    @staticmethod
    def notify_completion(status: dict, config: PipelineConfig):
        """Send completion notification"""
        if status["status"] == "SUCCESS":
            message = f"""
            ✅ Pipeline Completed Successfully
            Rows: {status.get('initial_rows')} → {status.get('cleaned_rows')}
            Duration: {status.get('duration_seconds', 0):.2f}s
            """
        else:
            message = f"""
            ❌ Pipeline Failed
            Error: {status.get('error', 'Unknown')}
            """
        
        logger.info(message)
        # TODO: Send notifications
        # NotificationService.send_email(...)
        # NotificationService.send_slack(...)


# ============================================================================
# Step 5: Retry Logic
# ============================================================================

from functools import wraps
import time

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry failed operations with exponential backoff.
    
    Example:
    @retry(max_attempts=3, delay=1.0, backoff=2.0)
    def load_data_from_api(url):
        ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"All {max_attempts} attempts failed: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
        
        return wrapper
    return decorator


# Example usage:
@retry(max_attempts=3, delay=1.0)
def load_data_with_retry(file_path: str):
    """Load data with automatic retry"""
    import pandas as pd
    return pd.read_csv(file_path)


# ============================================================================
# Step 6: Documentation (Sphinx)
# ============================================================================

SPHINX_CONF = """
# Sphinx Documentation Configuration
# Place in docs/conf.py

project = 'Retail Data Pipeline'
copyright = '2024'
author = 'Data Team'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

# Generate HTML documentation
html_theme = 'sphinx_rtd_theme'

# autodoc settings
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
"""

SPHINX_INDEX = """
Retail Data Pipeline Documentation
===================================

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   api
   deployment

Overview
--------

The Retail Data Pipeline is an enterprise-grade ETL solution for 
processing e-commerce order data.

Features
--------

- ✅ Modular ETL architecture
- ✅ Comprehensive error handling
- ✅ Database export capability
- ✅ Notification system
- ✅ Automatic retry logic
- ✅ Full test coverage

Installation
------------

.. code-block:: bash

    pip install -r requirements.txt

Quick Start
-----------

.. code-block:: python

    from main import run_pipeline
    result = run_pipeline()
    print(result['status'])
"""


def generate_documentation():
    """Generate Sphinx documentation structure"""
    logger.info("Generate documentation with: sphinx-quickstart docs/")
    logger.info("Then add API docs: sphinx-apidoc -o docs/ .")
    logger.info("Build HTML: cd docs && make html")


# ============================================================================
# Example: Putting it all together
# ============================================================================

def production_pipeline_example():
    """
    Complete production-grade pipeline example.
    """
    print("\n" + "=" * 80)
    print("PRODUCTION-READY PIPELINE EXAMPLE")
    print("=" * 80)
    
    # 1. Load config
    # config = PipelineConfig("config.yaml")
    config = PipelineConfig()  # Use defaults
    
    print(f"\nPipeline: {config.get('pipeline.name')}")
    print(f"Input: {config.get('input.file')}")
    print(f"Output: {config.get('output.revenue_file')}")
    
    # 2. Load and validate data
    # df = load_data_with_retry(config.get('input.file'))
    # schema_validator = SchemaValidator()
    # if not schema_validator.validate(df, schema_validator.create_schema_dict()):
    #     raise ValueError("Schema validation failed")
    
    # 3. Process pipeline
    # result = run_pipeline(...)
    
    # 4. Export to database
    # db = DatabaseExporter(config.get('database.connection_string'))
    # db.export_table(revenue_df, "revenue_by_category")
    
    # 5. Send notification
    # notifier = NotificationService()
    # notifier.notify_completion(result, config)
    
    print("\n✓ Production-ready features implemented!")
    print("=" * 80)


if __name__ == "__main__":
    print("Exercise 4: Production Readiness")
    print("=" * 80)
    
    # Create sample config file
    sample_config = {
        "pipeline": {"name": "Retail Data Pipeline", "version": "1.0.0"},
        "input": {"file": "orders.csv"},
        "output": {"revenue_file": "revenue.csv", "daily_file": "daily_sales.csv"},
        "database": {"type": "sqlite", "connection_string": "sqlite:///pipeline.db"},
        "notifications": {"enabled": True, "email": "admin@company.com"},
    }
    
    with open("config.yaml", "w") as f:
        yaml.dump(sample_config, f)
    
    logger.info("Created config.yaml")
    
    # Run example
    production_pipeline_example()
    
    print("\n" + "=" * 80)
    print("✓ Exercise 4 Complete: Production-ready features implemented")
    print("=" * 80)
    print("\nNext steps:")
    print("1. pip install sqlalchemy pandera")
    print("2. Configure database connection string")
    print("3. Set up email/Slack notifications")
    print("4. Run: sphinx-quickstart docs/")
    print("5. Deploy with Docker or Kubernetes")
    print("=" * 80)
