# Progress Bar Implementation for Multi-File Processing

## Overview
Added a visual progress bar to the Monitor GUI that shows real-time processing progress across multiple files.

## New Module: `NO_process_multiple_files_progress.py`

### Classes

#### `ProgressTracker`
Basic progress tracking for multi-file operations.

**Key Features:**
- Calculates total work units: `num_files × enabled_steps`
- Tracks completed work units
- Provides percentage and formatted text output
- Thread-safe when used with multiprocessing Manager

**Methods:**
```python
tracker = ProgressTracker(num_files=5, process_settings={...})
tracker.increment_progress(amount=1)
percentage = tracker.get_progress_percentage()  # Returns 0-100
text = tracker.get_progress_text()  # Returns "15/45 tasks (33%)"
```

#### `WeightedProgressTracker`
Enhanced tracker that weights steps by expected duration (optional, for future use).

**Step Weights:**
- Simulation: 3.0 (longest)
- Read Output: 2.0 (moderate)
- Visio: 1.5 (moderate)
- Excel: 1.0 (fast)
- Route: 1.0 (fast)

### Utility Functions

#### `calculate_progress_from_status(processing_dictionary, process_status_value_index)`
Calculates completed work by scanning the processing dictionary for "Done" status entries.

#### `get_step_weight(step_name)`
Returns weight multiplier for weighted progress tracking.

## Integration with Monitor_GUI

### Visual Components Added

1. **Progress Frame** (between Processing table and Error log)
   - Label showing "X/Y tasks (Z%)"
   - Horizontal progress bar (0-100%)
   - Updates every UPDATE_FREQUENCY ms

2. **Progress Updates**
   - Real-time: Scans processing_dictionary for completed tasks
   - Post-processing: Shows text messages for averaging/summary
   - Completion: Sets bar to 100% with "Complete!" message

### Code Changes

**`NO_process_multiple_files.py`:**

1. Import the progress module:
```python
import NO_process_multiple_files_progress as progress_tracker
```

2. Initialize in `Monitor_GUI.__init__()`:
```python
self.progress_tracker = progress_tracker.ProgressTracker(
    num_files=len(self.settings["ses_output_str"]), 
    self.process_settings
)
```

3. Add `update_progress_bar()` method that:
   - Calls `calculate_progress_from_status()`
   - Updates `self.progress_bar["value"]`
   - Updates `self.progress_label` text

4. Call from `update_monitor_table()`:
```python
self.update_progress_bar()
```

5. Special handling for post-processing:
```python
self.progress_label.config(text="Post-processing: Creating average output...")
# ... do work ...
self.progress_bar["value"] = 100
```

## How It Works

### Work Unit Calculation

Example: 5 files with settings `['Excel', 'Visio']`
- Total work units = 5 files × 2 steps = 10 tasks
- Each completed step increments progress by 1
- Progress = completed_tasks / total_tasks × 100%

### Progress Tracking Flow

1. **Initialization:** Calculate total work units from file count and enabled settings
2. **During Processing:** Monitor scans `processing_dictionary` for "Done" statuses
3. **Update Display:** Convert completed count to percentage, update bar and label
4. **Post-Processing:** Override label text for averaging/summary operations
5. **Completion:** Set to 100% and show completion message

### Thread Safety

- Uses multiprocessing.Manager() shared dictionary
- No locks needed - read-only access to `processing_dictionary`
- Progress bar updates only on GUI thread (via `self.after()`)

## Testing

Run the test suite:
```bash
python NO_process_multiple_files_progress.py
```

Expected output shows:
- Correct work unit calculation
- Percentage calculations at various completion levels
- Status dictionary parsing

## User Experience

**Before:**
- Users saw files moving through queued/processing/done lists
- No overall progress indication
- Unclear how much work remained

**After:**
- Clear progress percentage and task count
- Visual progress bar shows completion
- Post-processing status messages
- Better sense of remaining time

## Future Enhancements

1. **Weighted Progress** - Use `WeightedProgressTracker` to show more accurate progress (simulation takes longer than Excel export)

2. **Time Estimation** - Add estimated time remaining based on average task duration

3. **Per-File Progress** - Show progress within each file (e.g., "Parsing 50% of file.out")

4. **Pause/Resume Awareness** - Grey out progress bar when paused

5. **Color Coding** - Change progress bar color based on error count (green/yellow/red)

## Maintenance Notes

- Progress calculation assumes all files need same processing steps
- Does not account for files that fail early (they still count toward total)
- Post-processing (averaging/summary) not included in work units - shown as separate status
- Progress percentage may not be perfectly linear (parsing large files takes longer)
