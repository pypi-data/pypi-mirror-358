# Minimal Mode Demo

This demo shows the new simplified CLI mode for Co-DataScientist.

## Usage

### Minimal Mode (Default)
```bash
co-datascientist run --script-path /path/to/your/script.py --python-path python
```

**Output:**
```
🔬 Code Processing
───────────────────
ℹ️  Script: /path/to/your/script.py  
ℹ️  Python: python

⚡ Workflow Execution
──────────────────────
🌟 Minimal Mode: Use --debug for detailed logs

Workflow started successfully

Glowing up ✨

🚀 KPI: 0.7234

🚀 KPI: 0.7456

🚀 KPI: 0.7891

✅ Workflow completed successfully!
   🏆 Final Best Result: KPI = 0.7891 (iteration 47)
```

### Debug Mode (Verbose)
```bash
co-datascientist run --script-path /path/to/your/script.py --python-path python --debug
```

**Output:**
```
🔬 Code Processing
───────────────────
ℹ️  Script: /path/to/your/script.py  
ℹ️  Python: python

⚡ Workflow Execution
──────────────────────

Workflow started successfully

Generating idea 1/100

✅ Completed 'baseline' | KPI = 0.6892

Generating new idea...

✅ Completed 'evolve_gen_1_iter_0_prog_abc123...' | KPI = 0.7234
🚀 New best KPI: 0.7234 (evolve_gen_1_iter_0_prog_abc123...)

Generating new idea...

✅ Completed 'evolve_gen_1_iter_1_prog_def456...' | KPI = 0.7156

Generating new idea...

✅ Completed 'evolve_gen_1_iter_2_prog_ghi789...' | KPI = 0.7456
🚀 New best KPI: 0.7456 (evolve_gen_1_iter_2_prog_ghi789...)

... [continues with full details] ...
```

## Key Features

- **Minimal Mode**: Clean, simple output showing only KPI improvements
- **Debug Mode**: Full verbose logging with all execution details
- **Same underlying functionality**: Both modes save checkpoints, generate the same output files
- **Evolve Backend Support**: Optimized for the evolve engine workflow

## Benefits

- **Better UX**: No overwhelming logs for casual users
- **Fast feedback**: Immediately see when models improve
- **Debug when needed**: Full details available with `--debug` flag
- **Minimal code changes**: Existing functionality preserved 