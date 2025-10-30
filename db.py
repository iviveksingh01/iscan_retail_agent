# db.py
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
import os

def get_database_url():
    """Get DATABASE_URL from Streamlit secrets (cloud) or environment (local)."""
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
        else:
            raise KeyError
    except (ImportError, KeyError):
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("DATABASE_URL")

def execute_query(sql: str, max_rows: int = 1000):
    """Execute a SQL query and return results as list of dicts."""
    DATABASE_URL = get_database_url()
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not configured")

    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchmany(max_rows)
            result = []
            for row in rows:
                new_row = {}
                for key, value in row.items():
                    if isinstance(value, Decimal):
                        new_row[key] = float(value)
                    else:
                        new_row[key] = value
                result.append(new_row)
            return result
    except Exception as e:
        raise RuntimeError(f"Database error: {e}")
    finally:
        conn.close()