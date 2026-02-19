FROM continuumio/miniconda3:24.11.1-0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential cmake libfftw3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create conda environment with Python 3.10 and GROMACS
RUN conda install -c conda-forge -y \
    python=3.10 \
    gromacs=2025.4 \
    mpi4py \
    numpy \
    networkx \
    packaging \
    && conda clean -afy

# Install Python MCP dependencies
RUN pip install --no-cache-dir \
    fastmcp \
    loguru \
    pandas

# Verify GROMACS installation (acts as a build-time checkpoint)
RUN gmx --version | head -3

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY configs/ ./configs/
COPY examples/ ./examples/
RUN mkdir -p jobs tmp/inputs tmp/outputs results

ENV PYTHONPATH=/app

CMD ["python", "src/server.py"]
