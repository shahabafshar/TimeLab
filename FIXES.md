# Bug Fixes Applied

## Issue 1: SQLAlchemy Reserved Name Conflict ✅ FIXED

**Error:**
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

**Root Cause:**
- The `Dataset` model had a column named `metadata`
- SQLAlchemy's Declarative API reserves `metadata` for internal use

**Fix:**
- Renamed column from `metadata` to `meta_data` in `backend/app/models/dataset.py`
- Updated API code to use `meta_data` when creating Dataset instances
- Created migration file for existing databases

**Files Changed:**
- `backend/app/models/dataset.py` - Column renamed to `meta_data`
- `backend/app/api/v1/datasets.py` - Updated to use `meta_data`
- `backend/alembic/versions/001_rename_metadata_column.py` - Migration file

## Issue 2: Pydantic v2 Config Conflict ✅ FIXED

**Error:**
```
pydantic.errors.PydanticUserError: "Config" and "model_config" cannot be used together
```

**Root Cause:**
- Pydantic v2 doesn't allow both `class Config:` and `model_config` together
- We had both in `ProjectResponse` and other schemas

**Fix:**
- Converted all schemas to use Pydantic v2 syntax with `ConfigDict`
- Replaced `class Config:` with `model_config = ConfigDict(...)`
- Combined `protected_namespaces` and `from_attributes` in single `ConfigDict`

**Files Changed:**
- `backend/app/schemas/project.py` - Converted to `ConfigDict`
- `backend/app/schemas/dataset.py` - Converted to `ConfigDict`
- `backend/app/schemas/model.py` - Converted to `ConfigDict`

**Before:**
```python
class ProjectResponse(BaseModel):
    ...
    model_config = {"protected_namespaces": ()}
    
    class Config:
        from_attributes = True
```

**After:**
```python
class ProjectResponse(BaseModel):
    ...
    model_config = ConfigDict(
        protected_namespaces=(),
        from_attributes=True
    )
```

## Testing

After these fixes, the backend should start without errors:

```bash
cd backend
.\run-backend.bat
# or
.\run-backend.ps1
```

The server should start successfully at http://localhost:8000

## Summary

✅ SQLAlchemy reserved name conflict fixed  
✅ Pydantic v2 config syntax updated  
✅ All schemas now use proper Pydantic v2 syntax  
✅ Migration file created for database updates  
