# CLI Changes Summary

## Overview
Added a `--debug` flag to control CLI verbosity, providing a clean minimal mode by default and verbose debug mode when needed.

## Changes Made

### 1. CLI Interface (`cli.py`)
- **Added `--debug` flag** to the `run` command
- **Default behavior**: Minimal mode (debug=False)
- **Debug mode**: Full verbose logging (debug=True)
- **Updated help text**: "Show detailed logs (default: minimal output)"

### 2. Workflow Runner (`workflow_runner.py`)
- **Updated `run_workflow()` method** to accept `debug` parameter
- **Added `debug_mode` instance variable** to track current mode
- **Created `_handle_minimal_mode_result()`** for simple output
- **Updated `_run_sequential_mode()`** to support minimal mode
- **Modified `BatchExecutor`** to respect debug mode

### 3. Output Control
**Minimal Mode (default):**
- Shows "Glowing up ✨" spinner
- Only displays rocket emoji + KPI for improvements: `🚀 KPI: 0.7234`
- Hides verbose execution details
- Still saves all checkpoints and files

**Debug Mode (`--debug`):**
- Shows all existing verbose output
- Detailed execution logs
- Timing information
- Error details
- Batch processing info

### 4. Batch Mode Support
- **Updated `BatchExecutor`** constructor to accept `debug` parameter
- **Conditional logging** for parallel execution details
- **Hidden timing output** in minimal mode
- **Simplified error handling** in minimal mode

## Key Features

✅ **Minimal changes**: Existing functionality preserved  
✅ **Backward compatible**: Debug mode maintains current behavior  
✅ **Evolve backend optimized**: Works great with evolve workflows  
✅ **Clean UX**: Simple output for casual users  
✅ **Debug available**: Full details when needed  

## Usage Examples

```bash
# Minimal mode (default)
co-datascientist run --script-path script.py --python-path python

# Debug mode (verbose)
co-datascientist run --script-path script.py --python-path python --debug

# Works with all existing options
co-datascientist run --script-path script.py --python-path python --best-only --debug
```

## Files Modified
1. `src/co_datascientist/cli.py` - Added --debug flag
2. `src/co_datascientist/workflow_runner.py` - Added minimal mode logic

## Testing
- Test both minimal and debug modes
- Verify checkpoint saving works in both modes
- Ensure batch mode respects debug setting
- Check that KPI improvements are shown correctly 