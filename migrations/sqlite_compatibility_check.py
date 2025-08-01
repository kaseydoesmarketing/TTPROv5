#!/usr/bin/env python3
"""
SQLite Compatibility Check Script

This script validates that database schemas are compatible with SQLite
and prevents deployment of incompatible changes.
"""

import sqlite3
import sys
from pathlib import Path

def check_sqlite_functions(schema_content, filename=""):
    """Check for incompatible SQL functions in schema"""
    incompatible_functions = [
        'NOW()',
        'CURRENT_TIMESTAMP()',  # PostgreSQL style
        'GETDATE()',  # SQL Server
        'SYSDATE()',  # Oracle
    ]
    
    # Skip documentation files and this script itself
    if any(name in filename for name in ['README', 'compatibility_check.py']):
        return []
    
    issues = []
    lines = schema_content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments and docstrings
        line_stripped = line.strip()
        if line_stripped.startswith('#') or line_stripped.startswith('"""') or line_stripped.startswith("'''"):
            continue
            
        for func in incompatible_functions:
            if func.lower() in line.lower():
                # Check if it's in actual code (not in strings or comments)
                if not ('"""' in line or "'''" in line or '#' in line.split(func.lower())[0]):
                    # Exclude Python datetime.utcnow() calls
                    if 'datetime.' not in line and 'utcnow' not in line:
                        # Check if it's in a SQL context (server_default, etc.)
                        if any(sql_context in line for sql_context in ['server_default', 'default=', 'Column(']):
                            issues.append(f"Found incompatible function {func} in {filename}:{line_num}")
    
    return issues

def validate_schema_file(schema_file):
    """Validate a schema file for SQLite compatibility"""
    if not schema_file.exists():
        return [f"Schema file not found: {schema_file}"]
    
    content = schema_file.read_text()
    return check_sqlite_functions(content, str(schema_file))

def main():
    """Main validation function"""
    backend_dir = Path(__file__).parent.parent
    
    # Check model definitions
    models_file = backend_dir / "app" / "models.py"
    issues = validate_schema_file(models_file)
    
    # Check any migration files
    migrations_dir = backend_dir / "migrations"
    if migrations_dir.exists():
        for migration_file in migrations_dir.glob("*.sql"):
            issues.extend(validate_schema_file(migration_file))
    
    if issues:
        print("❌ SQLite Compatibility Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n💡 Recommended fixes:")
        print("  - Replace NOW() with datetime('now')")
        print("  - Use SQLite-compatible datetime functions")
        sys.exit(1)
    else:
        print("✅ All schemas are SQLite compatible")

if __name__ == "__main__":
    main()