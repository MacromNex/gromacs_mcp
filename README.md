# GROMACS MCP Server

**Molecular dynamics simulation using GROMACS 2025.4 via Docker**

An MCP (Model Context Protocol) server for GROMACS molecular dynamics with 6 core tools:
- Run GROMACS commands and analyze TPR files
- Execute predefined simulation workflows
- Submit long-running MD simulations with async job tracking
- Batch analyze multiple molecular systems
- Monitor and retrieve simulation results
- List available GROMACS commands and workflows

## Quick Start with Docker

### Approach 1: Pull Pre-built Image from GitHub

The fastest way to get started. A pre-built Docker image is automatically published to GitHub Container Registry on every release.

```bash
# Pull the latest image
docker pull ghcr.io/macromnex/gromacs_mcp:latest

# Register with Claude Code (runs as current user to avoid permission issues)
claude mcp add gromacs -- docker run -i --rm --user `id -u`:`id -g` -v `pwd`:`pwd` ghcr.io/macromnex/gromacs_mcp:latest
```

**Note:** Run from your project directory. `` `pwd` `` expands to the current working directory.

**Requirements:**
- Docker
- Claude Code installed

That's it! The GROMACS MCP server is now available in Claude Code.

---

### Approach 2: Build Docker Image Locally

Build the image yourself and install it into Claude Code. Useful for customization or offline environments.

```bash
# Clone the repository
git clone https://github.com/MacromNex/gromacs_mcp.git
cd gromacs_mcp

# Build the Docker image
docker build -t gromacs_mcp:latest .

# Register with Claude Code (runs as current user to avoid permission issues)
claude mcp add gromacs -- docker run -i --rm --user `id -u`:`id -g` -v `pwd`:`pwd` gromacs_mcp:latest
```

**Note:** Run from your project directory. `` `pwd` `` expands to the current working directory.

**Requirements:**
- Docker
- Claude Code installed
- Git (to clone the repository)

**About the Docker Flags:**
- `-i` — Interactive mode for Claude Code
- `--rm` — Automatically remove container after exit
- `` --user `id -u`:`id -g` `` — Runs the container as your current user, so output files are owned by you (not root)
- `-v` — Mounts your project directory so the container can access your data

---

## Verify Installation

After adding the MCP server, you can verify it's working:

```bash
# List registered MCP servers
claude mcp list

# You should see 'gromacs' in the output
```

In Claude Code, you can now use all 6 GROMACS tools:
- `run_gromacs_command`
- `run_gromacs_workflow`
- `submit_md_simulation`
- `submit_batch_analysis`
- `get_job_status`
- `get_job_result`

---

## Next Steps

- **Detailed documentation**: See [detail.md](detail.md) for comprehensive guides on:
  - Available MCP tools and parameters
  - Local Python environment setup (alternative to Docker)
  - Example workflows and use cases
  - Configuration file options
  - GROMACS command reference

---

## Usage Examples

Once registered, you can use the GROMACS tools directly in Claude Code. Here are some common workflows:

### Example 1: Analyze a Simulation File

```
I have a GROMACS TPR file at /path/to/simulation.tpr. Can you use run_gromacs_command with the dump command to analyze what's in the file and show me the simulation parameters?
```

### Example 2: Run a Short MD Simulation

```
I want to test my GROMACS setup with a short MD run. Can you use submit_md_simulation with the TPR file at /path/to/system.tpr for 1000 steps and save the outputs to /path/to/results/? Monitor the job until it finishes.
```

### Example 3: Batch Analysis of Multiple Systems

```
I have several TPR files in /path/to/simulations/ directory. Can you submit batch analysis using submit_batch_analysis to extract energetics and structural parameters from all of them, saving results to /path/to/analysis/?
```

---

## Troubleshooting

**Docker not found?**
```bash
docker --version  # Install Docker if missing
```

**Claude Code not found?**
```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code
```

**GROMACS not working inside container?**
- The container includes GROMACS 2025.4 pre-installed
- Verify with: `docker run --rm ghcr.io/macromnex/gromacs_mcp:latest gmx --version`

---

## License

LGPL (GROMACS)
