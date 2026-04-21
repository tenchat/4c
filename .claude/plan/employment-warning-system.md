# Employment Warning System - Bug Fix Plan

## Current Issues

1. **Backend**: `/warnings` API missing `warning_type` query parameter
2. **Backend**: Dead code in `school_service.py` lines 991-994
3. **Frontend**: Pagination not working (always page 1, size 10)
4. **Frontend**: Warning type shows raw enum `unemployed_long_term` instead of mapped Chinese text
5. **Frontend**: Table width doesn't fill container

## Root Cause Analysis

### Backend Bug #1 - Missing `warning_type` Parameter
```python
# school.py:243-252 - current code
@router.get("/warnings")
async def get_warnings(
    ...
    handled: bool = None,
    level: int = None
    # ❌ MISSING: warning_type: str = None
):
```
The API accepts `handled` and `level` but NOT `warning_type`, even though `school_service.get_warnings()` handles it.

### Backend Bug #2 - Dead Code
```python
# school_service.py:991-994 - orphaned code after return statement
        await self.db.commit()
        return True

    async def get_databoard_data(...)  # ❌ DEAD CODE - unreachable
```

### Frontend Bug #1 - Pagination
The `useTable` hook correctly handles pagination. Check if `ArtTable` is properly wiring `@pagination:size-change` and `@pagination:current-change`.

### Frontend Bug #2 - Warning Type Display
The backend stores `warning_type` as string enum like `"unemployed_long_term"`. The frontend's `WARNING_TYPE_MAP` should display Chinese text. Issue might be:
- Backend returning wrong structure, OR
- Formatter not receiving correct field

### Frontend Bug #3 - Table Width
```vue
<!-- Current -->
<ArtTable :loading="loading" :data="data" :columns="columns" :pagination="pagination" />

<!-- Need to ensure table stretches -->
.art-table-card { width: 100%; }
```

---

## Implementation Steps

### Step 1: Fix Backend - Add `warning_type` Parameter

**File**: `backend/app/api/v1/school.py`

At line ~250, add `warning_type` to query parameters:

```python
@router.get("/warnings")
async def get_warnings(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    handled: bool = None,
    level: int = None,
    warning_type: str = None,  # ✅ ADD THIS
):
```

And in the filters dict:
```python
filters = {
    "page": page,
    "page_size": page_size,
    "handled": handled,
    "level": level,
    "warning_type": warning_type,  # ✅ ADD THIS
}
```

### Step 2: Fix Backend - Remove Dead Code

**File**: `backend/app/services/school_service.py`

Delete lines 991-994 (the orphaned `handle_warning` continuation after `return True`).

### Step 3: Verify Frontend Pagination Wiring

**File**: `src/views/school/warnings/index.vue`

Check that ArtTable properly emits events:
```vue
<ArtTable
  :loading="loading"
  :data="data"
  :columns="columns"
  :pagination="pagination"
  @selection-change="handleSelectionChange"
  @pagination:size-change="handleSizeChange"   <!-- ✅ Should be wired -->
  @pagination:current-change="handleCurrentChange"  <!-- ✅ Should be wired -->
/>
```

The `handleSizeChange` and `handleCurrentChange` are exported from `useTable` and should work.

### Step 4: Verify Warning Type Formatter

**File**: `src/views/school/warnings/index.vue`

The formatter at line ~223:
```typescript
formatter: (row: WarningItem) =>
  WARNING_TYPE_MAP[row.warning_type] || row.warning_type || '未知'
```

Ensure `row.warning_type` contains the expected string value. If backend returns `{ warning_type: "unemployed_long_term" }`, this should work.

### Step 5: Fix Table Width

**File**: `src/views/school/warnings/index.vue`

Add CSS:
```css
<style scoped>
.art-table-card {
  width: 100%;
}
</style>
```

---

## Files to Modify

| File | Change | Lines |
|------|--------|-------|
| `backend/app/api/v1/school.py` | Add `warning_type` query param | ~250 |
| `backend/app/services/school_service.py` | Delete dead code | 991-994 |
| `src/views/school/warnings/index.vue` | CSS fix for table width | ~461 |

---

## Verification

After fixes:
1. Call `GET /api/v1/school/warnings?warning_type=unemployed_long_term` - should filter correctly
2. Pagination size/current changes should reflect in API calls
3. Warning type should display Chinese text "长期未就业"
4. Table should fill container width
