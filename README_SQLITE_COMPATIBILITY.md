# SQLite Compatibility Guide

This document outlines the measures in place to prevent SQLite compatibility issues.

## Prevention Measures

### 1. Database Utility Functions
- **File**: `app/database_utils.py`
- **Purpose**: Provides SQLite-compatible datetime functions
- **Usage**: Always use `get_sqlite_compatible_datetime()` instead of `func.now()`

### 2. Compatibility Validation Script
- **File**: `migrations/sqlite_compatibility_check.py`
- **Purpose**: Validates schema files for SQLite compatibility
- **Usage**: Run manually or as part of CI/CD pipeline

### 3. Pre-commit Hook
- **File**: `pre-commit-hook.py`
- **Purpose**: Automatically checks compatibility before commits
- **Setup**: Copy to `.git/hooks/pre-commit` and make executable

### 4. Startup Validation
- **File**: `app/startup.py`
- **Purpose**: Validates database schema on application startup
- **Integration**: Called during app initialization

## Common SQLite Incompatibilities

### ❌ Avoid These:
```python
# PostgreSQL/MySQL style - DON'T USE
created_at = Column(DateTime, server_default=func.now())
```

### ✅ Use These Instead:
```python
# SQLite compatible - USE THIS
from app.database_utils import get_sqlite_compatible_datetime
created_at = Column(DateTime, server_default=get_sqlite_compatible_datetime())
```

## Functions to Avoid in SQLite

| Function | Database | SQLite Alternative |
|----------|----------|-------------------|
| `NOW()` | MySQL/PostgreSQL | `datetime('now')` |
| `CURRENT_TIMESTAMP()` | PostgreSQL | `datetime('now')` |
| `GETDATE()` | SQL Server | `datetime('now')` |
| `SYSDATE()` | Oracle | `datetime('now')` |

## Development Workflow

1. **Before making model changes**: Run compatibility check
   ```bash
   python migrations/sqlite_compatibility_check.py
   ```

2. **After modifying models**: The pre-commit hook will automatically validate

3. **During deployment**: Startup checks will validate the production database

## Troubleshooting

### Issue: "unknown function: now()"
**Cause**: Database schema contains incompatible datetime functions
**Solution**: 
1. Run the compatibility check script
2. Update the database schema using the generated migration
3. Restart the application

### Issue: Pre-commit hook fails
**Cause**: Model changes introduce SQLite incompatibilities
**Solution**:
1. Review the error messages
2. Update model definitions to use compatible functions
3. Re-commit changes

## Manual Schema Updates

If you need to manually update the database schema:

```sql
-- Example: Fix youtube_channels table
BEGIN TRANSACTION;
CREATE TABLE youtube_channels_new (
    -- ... column definitions with correct defaults ...
    created_at DATETIME DEFAULT (datetime('now')),
    updated_at DATETIME DEFAULT (datetime('now'))
);
INSERT INTO youtube_channels_new SELECT * FROM youtube_channels;
DROP TABLE youtube_channels;
ALTER TABLE youtube_channels_new RENAME TO youtube_channels;
COMMIT;
```

## Best Practices

1. **Always use utility functions** for datetime defaults
2. **Test with SQLite** during development
3. **Run compatibility checks** before deploying
4. **Keep this documentation updated** when adding new prevention measures

## Integration with CI/CD

Add to your CI pipeline:
```yaml
- name: Check SQLite Compatibility
  run: python backend/migrations/sqlite_compatibility_check.py
```