<div align="center">
  <img width="300" height="300" src="https://i.imgur.com/KISXGnH.png" alt="Chisel CLI logo" /> 
	<h1>chisel</h1>
</div>

**TL;DR:** Seamless GPU kernel profiling on cloud infrastructure. Write GPU code, run one command, get profiling results. Zero GPU hardware required.

> 🚀 **Recent Releases**
> 
> ### Latest
> - **AMD rocprofv3 Support**: Full integration with AMD's latest profiling tool
> - **Automatic Cleanup**: Remote files are automatically cleaned up after profiling

> 🔮 **Upcoming Features**
> 
> ### In Development
> - **Python Support**: Direct profiling of Python GPU applications (PyTorch, TensorFlow, etc.)
> - **Web Dashboard**: Browser-based visualization of profiling results.
> - **Multi-GPU Support**: Profile the same kernel across multiple GPU types simultaneously.
> - **Profiling Backend**: Bypass the need for a DigitalOcean account by using a public backend.

## Quick Start

Get up and running in 30 seconds:

```bash
# 1. Install chisel
pip install chisel-cli

# 2. Configure with your DigitalOcean API token
chisel configure

# 3. Profile your GPU kernels
chisel profile nvidia kernel.cu    # NVIDIA H100
chisel profile amd kernel.cpp      # AMD MI300X
```

**That's it!** 🚀 No GPU hardware needed—develop and profile GPU kernels from any machine.

> **Need a DigitalOcean API token?** Get one [here](https://amd.digitalocean.com/account/api/tokens) (requires read/write access).

## Commands

Chisel has just **3 commands**:

### `chisel configure`

One-time setup of your DigitalOcean API credentials.

```bash
# Interactive configuration
chisel configure

# Non-interactive with token
chisel configure --token YOUR_TOKEN
```

### `chisel profile nvidia <file_or_command>`

Profile GPU kernels on NVIDIA H100 ($4.89/hour) or L40S ($2.21/hour).

```bash
# Compile and profile CUDA source files
chisel profile nvidia matrix.cu              # Default: H100
chisel profile nvidia kernel.cu --gpu-type l40s  # L40S GPU

# Profile existing binaries or commands
chisel profile nvidia "./my-cuda-app --size=1024"
chisel profile nvidia "nvidia-smi"
```

### `chisel profile amd <file_or_command>`

Profile GPU kernels on AMD MI300X ($1.99/hour).

```bash
# Compile and profile HIP source files
chisel profile amd matrix.cpp
chisel profile amd kernel.hip

# Profile with performance counters
chisel profile amd matrix.cpp --pmc "GRBM_GUI_ACTIVE,SQ_WAVES,SQ_BUSY_CYCLES"

# Profile existing binaries or commands
chisel profile amd "./my-hip-app --iterations=100"
chisel profile amd "rocm-smi"
```

## Examples

### AMD Profiling

```bash
# Create a simple HIP kernel
cat > simple.cpp << 'EOF'
#include <hip/hip_runtime.h>
#include <iostream>

__global__ void add_kernel(int *a, int *b, int *c, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        c[idx] = a[idx] + b[idx];
    }
}

int main() {
    // Your HIP code here
    std::cout << "HIP kernel executed!" << std::endl;
    return 0;
}
EOF

# Profile it
chisel profile amd simple.cpp

# Profile with performance counters
chisel profile amd simple.cpp --pmc "GRBM_GUI_ACTIVE,SQ_WAVES"

# Get a human-readable summary table showing:
# - HIP/HSA API calls with timing breakdown
# - Kernel execution statistics
# - Memory operations and bandwidth analysis
# - Performance counter data (when --pmc used)
```

### NVIDIA Profiling

```bash
# Create a simple CUDA kernel
cat > simple.cu << 'EOF'
#include <cuda_runtime.h>
#include <iostream>

__global__ void multiply_kernel(int *a, int *b, int *c, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        c[idx] = a[idx] * b[idx];
    }
}

int main() {
    // Your CUDA code here
    std::cout << "CUDA kernel executed!" << std::endl;
    return 0;
}
EOF

# Profile it
chisel profile nvidia simple.cu

# Get a human-readable summary table showing:
# - CUDA kernels with execution time and call counts
# - Memory operations and bandwidth analysis
# - API call timing breakdown
```

**Results are saved to:** `chisel-results/TIMESTAMP/profile_summary.txt`

## GPU Support

| GPU         | Size                | Region | Cost/Hour | Profiling                       |
| ----------- | ------------------- | ------ | --------- | ------------------------------- |
| NVIDIA H100 | `gpu-h100x1-80gb`   | NYC2   | $4.89     | nsight-compute + nsight-systems |
| NVIDIA L40S | `gpu-l40sx1-48gb`   | TOR1   | $2.21     | nsight-compute + nsight-systems |
| AMD MI300X  | `gpu-mi300x1-192gb` | ATL1   | $1.99     | rocprofv3                       |

## Development Setup

```bash
# With uv (recommended)
uv sync
uv run chisel <command>

# With pip
pip install -e .
```

## Making updates to PyPI

```bash
rm -rf dist/ build/ *.egg-info && python -m build && twine upload dist/*
```

## Testing

```bash
chisel profile --rocprofv3="--sys-trace" examples/simple-mm.hip
```
