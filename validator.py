# validator.py
import sqlglot
from sqlglot import expressions as exp

ALLOWED_TABLES = {"store_scores"}

def is_safe_sql(sql: str) -> bool:
    try:
        parsed = sqlglot.parse_one(sql, dialect="postgres")
        
        # Must be a SELECT statement
        if not isinstance(parsed, exp.Select):
            return False

        # Block dangerous statement types by name (safe for old sqlglot)
        dangerous_types = {"Delete", "Update", "Insert", "Drop", "Alter", "Create"}
        parsed_type = type(parsed).__name__
        if parsed_type in dangerous_types:
            return False

        # Extract table names (handle schema)
        tables_used = set()
        for node in parsed.walk():
            if isinstance(node, exp.Table):
                tables_used.add(node.name.lower())

        allowed_lower = {t.lower() for t in ALLOWED_TABLES}
        if not tables_used.issubset(allowed_lower):
            return False

        return True

    except Exception as e:
        print(f"[DEBUG] SQL validation error: {e}")
        return False