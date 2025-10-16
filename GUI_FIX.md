# GUI Fix: Async UI Updates from Background Threads

## Issue
When running conversions in the GUI, the app crashed with:
```
AssertionError in page.run_task()
assert asyncio.iscoroutinefunction(handler)
```

## Root Cause
The `page.run_task()` method in Flet requires an **async coroutine function**, but we were passing regular lambda functions:

```python
# BROKEN - lambda is not async
self.page.run_task(lambda: self._update_job_ui(job))
```

## Solution
Wrap UI update calls in async functions:

```python
# FIXED - wrapped in async function
async def update_ui():
    self._update_job_ui(job)
self.page.run_task(update_ui)
```

## Changes Made

**File: `src/file_converter/ui/pages/run_queue.py`**

### Before:
```python
def on_update(job):
    self.page.run_task(lambda: self._update_job_ui(job))

# Later...
self.page.run_task(lambda: self._on_run_complete())
```

### After:
```python
def on_update(job):
    async def update_ui():
        self._update_job_ui(job)
    self.page.run_task(update_ui)

# Later...
async def complete_ui():
    self._on_run_complete()
self.page.run_task(complete_ui)
```

## Why This Works
1. Background thread runs conversions via `threading.Thread`
2. When progress updates occur, we need to update the UI
3. Flet requires UI updates from background threads to use `page.run_task()`
4. `page.run_task()` expects an async coroutine to safely marshal the call to the main event loop
5. Our async wrappers provide the coroutine wrapper around our synchronous UI update methods

## Testing
- ✅ Integration test passes (conversion engine works)
- ✅ GUI should now handle queue runs without crashes
- ✅ Progress updates will display correctly

## Usage
After this fix, you can:
1. Add files to the queue in the Home tab
2. Switch to Run Queue tab
3. Click "Run Queue"
4. Watch real-time progress updates
5. See completion status when done

No more AssertionError crashes!

