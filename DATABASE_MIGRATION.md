# Database Migration Guide

## Issue
Database schema is outdated - missing `scoring_version` column in `analyses` table.

## Error
```
sqlite3.OperationalError: table analyses has no column named scoring_version
```

## Solution

### Option 1: Recreate Database (Development - RECOMMENDED)

```powershell
# 1. Stop backend (Ctrl+C in uvicorn terminal)

# 2. Delete old database
Remove-Item backend/dev_seo_analyzer.db

# 3. Restart backend (will auto-create new schema)
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Option 2: Manual Migration (Preserves Data)

```powershell
# 1. Backup existing database
Copy-Item backend/dev_seo_analyzer.db backend/dev_seo_analyzer.db.backup

# 2. Run migration script
cd backend
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Note: SQLite doesn't support ALTER COLUMN, so this won't work
# You'll need to manually add the column via SQL
```

### Option 3: SQL Migration (Manual)

```sql
-- Connect to database
sqlite3 backend/dev_seo_analyzer.db

-- Add column
ALTER TABLE analyses ADD COLUMN scoring_version TEXT DEFAULT '1.0.0';

-- Verify
.schema analyses
```

## Verification

After migration, test analysis creation:
```powershell
curl http://localhost:8000/api/analysis/create `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"keyword":"test","language":"en","location":"US"}'
```

## Files Changed (Phase 3)
- `backend/database.py` - added `scoring_version` column
- Schema now includes versioning for all analyses
