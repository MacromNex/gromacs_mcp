# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

MCP server exposing GROMACS 2025.4 molecular dynamics tools via FastMCP. Provides 13 tools: sync operations (analyze_tpr, run_gromacs_command, run_gromacs_workflow), async job submission (submit_md_simulation, submit_batch_analysis), job management (get/cancel/list jobs), and info tools.

## Build & Run

```bash
# Full setup from scratch
bash quick_setup.sh

# Run the MCP server
./env/bin/python src/server.py

# Dev mode (hot reload + inspector)
fastmcp dev src/server.py

# Register with Claude Code
claude mcp add gromacs-2025.4 -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

### Docker

```bash
docker build -t gromacs-mcp .
docker run gromacs-mcp
```

## Testing

```bash
# Unit tests (pytest)
./env/bin/python -m pytest tests/test_server.py -v

# Integration tests (custom runner, outputs JSON report)
./env/bin/python tests/run_integration_tests.py

# Direct tool validation against sample data
./env/bin/python tests/validate_mcp_tools.py

# Basic server startup test
./env/bin/python test_mcp_client.py
```

## Architecture

### Dual API Pattern

Every GROMACS capability has two interfaces sharing the same core logic:
- **CLI** (`scripts/*.py`): Standalone argparse scripts runnable directly
- **MCP** (`src/server.py`): FastMCP tool wrappers that call into the scripts

Shared utilities live in `scripts/lib/gromacs_utils.py` (subprocess execution, gmx binary discovery, TPR parsing).

### Sync vs Async Tools

Sync tools (`analyze_tpr`, `run_gromacs_command`, `run_gromacs_workflow`) call scripts directly and return results immediately.

Submit tools (`submit_md_simulation`, `submit_batch_analysis`) use `src/jobs/manager.py` to run scripts in background threads via `mamba run -p ./env`. Jobs persist metadata as JSON in `jobs/<job_id>/` directories. Job lifecycle: PENDING → RUNNING → COMPLETED/FAILED/CANCELLED.

### GROMACS Binary Discovery

`scripts/lib/gromacs_utils.py:find_gromacs_command()` tries system `gmx` first, falls back to `mamba run -p ./env gmx`. The `configs/default_config.json` defines `command_prefix` and `fallback_command` for this.

### Result Convention

All tool functions return `dict` with `"status": "success"|"error"`. Use `src/utils.py:format_tool_result()` to wrap results consistently.

### Configuration Layering

Each script has an embedded `DEFAULT_CONFIG` dict. Overrides come from: JSON config files (`--config` CLI flag) → function kwargs → defaults.

## Key Files

- `src/server.py` — All 13 MCP tool definitions
- `src/jobs/manager.py` — Thread-based job executor with log capture
- `src/utils.py` — validate_input_file, setup_output_directory, format_tool_result, configure_logging
- `scripts/lib/gromacs_utils.py` — find_gromacs_command, run_command, parse_tpr_dump_output
- `configs/default_config.json` — Global config (timeouts, paths, performance limits)
- `examples/data/sample.tpr` — 1000 Argon atoms test system used by all tests

## Dependencies

Runtime: `fastmcp`, `loguru`, GROMACS 2025.4 (via conda-forge). Python 3.10+. Conda/mamba for environment management.
