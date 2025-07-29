<div align="center">
  <img width="300" height="300" src="https://i.imgur.com/KISXGnH.png" alt="Chisel CLI logo" /> 
	<h1>chisel</h1>
</div>

**TL;DR:** Seamless GPU kernel profiling on cloud infrastructure. Write GPU code, run one command, get profiling results. Zero GPU hardware required.

> 🚀 **Recent Releases**
> 
> ### Latest
> - **Python Support**: Direct profiling of Python GPU applications (PyTorch, TensorFlow, etc.)
> - **AMD rocprofv3 Support**: Full integration with AMD's latest profiling tool
> - **Automatic Cleanup**: Remote files are automatically cleaned up after profiling

> 🔮 **Upcoming Features**
> 
> ### In Development
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
chisel profile --nsys kernel.cu              # NVIDIA with nsys
chisel profile --rocprofv3 kernel.cpp        # AMD with rocprofv3
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

### `chisel profile --nsys="<nsys flags>" <file>`

Profile GPU kernels on NVIDIA H100 ($4.89/hour) or L40S ($2.21/hour).

```bash
chisel profile --nsys="--trace=cuda --cuda-memory-usage=true" examples/kernel.cu
```

### `chisel profile --ncompute="<ncu flags>" <file>`

```bash
chisel profile --ncompute="--metrics all" examples/kernel.cu
```

### `chisel profile --rocprofv3="<rocprofv3 flags>" <file>`

Profile GPU kernels on AMD MI300X ($1.99/hour).

```bash
chisel profile --rocprofv3="--sys-trace" examples/attention_block.py
chisel profile --rocprofv3="--sys-trace" examples/simple-mm.hip
```

## Examples

### Python GPU Applications

```bash
# Create a PyTorch training script
cat > train.py << 'EOF'
import torch
import torch.nn as nn
import time

# Simple neural network
model = nn.Sequential(
    nn.Linear(1024, 512),
    nn.ReLU(),
    nn.Linear(512, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
).cuda()

# Generate some data
x = torch.randn(1000, 1024).cuda()
y = torch.randint(0, 10, (1000,)).cuda()

# Training loop
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()

for epoch in range(5):
    output = model(x)
    loss = criterion(output, y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch}, Loss: {loss.item()}")
EOF

# Profile PyTorch on NVIDIA

# Profile PyTorch on AMD  
chisel profile --rocprofv3 train.py

# Get detailed kernel analysis showing:
# - GPU kernel execution times and memory usage
# - CUDA/HIP API call timing breakdown
# - Memory transfer analysis
# - Optimization suggestions
```

### AMD HIP Profiling

```bash
# Create a simple HIP kernel
cat > matrix_add.cpp << 'EOF'
#include <hip/hip_runtime.h>
#include <iostream>
#include <vector>

__global__ void matrixAdd(float *A, float *B, float *C, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    int j = blockIdx.y * blockDim.y + threadIdx.y;
    
    if (i < N && j < N) {
        int idx = i * N + j;
        C[idx] = A[idx] + B[idx];
    }
}

int main() {
    const int N = 1024;
    size_t size = N * N * sizeof(float);
    
    // Allocate and run kernel
    float *d_A, *d_B, *d_C;
    hipMalloc(&d_A, size);
    hipMalloc(&d_B, size);
    hipMalloc(&d_C, size);
    
    dim3 threadsPerBlock(16, 16);
    dim3 numBlocks((N + threadsPerBlock.x - 1) / threadsPerBlock.x,
                   (N + threadsPerBlock.y - 1) / threadsPerBlock.y);
    
    hipLaunchKernelGGL(matrixAdd, numBlocks, threadsPerBlock, 0, 0, d_A, d_B, d_C, N);
    hipDeviceSynchronize();
    
    std::cout << "Matrix addition completed!" << std::endl;
    return 0;
}
EOF

# Profile with detailed system tracing
chisel profile --rocprofv3="--sys-trace" matrix_add.cpp
```

### NVIDIA CUDA Profiling

```bash
# Create a CUDA matrix multiplication kernel
cat > matmul.cu << 'EOF'
#include <cuda_runtime.h>
#include <cublas_v2.h>
#include <iostream>

__global__ void matmul_kernel(float *A, float *B, float *C, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (row < N && col < N) {
        float sum = 0.0f;
        for (int k = 0; k < N; k++) {
            sum += A[row * N + k] * B[k * N + col];
        }
        C[row * N + col] = sum;
    }
}

int main() {
    const int N = 1024;
    size_t size = N * N * sizeof(float);
    
    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, size);
    cudaMalloc(&d_B, size);
    cudaMalloc(&d_C, size);
    
    dim3 threadsPerBlock(16, 16);
    dim3 numBlocks((N + 15) / 16, (N + 15) / 16);
    
    matmul_kernel<<<numBlocks, threadsPerBlock>>>(d_A, d_B, d_C, N);
    cudaDeviceSynchronize();
    
    std::cout << "Matrix multiplication completed!" << std::endl;
    return 0;
}
EOF

```

**Results are saved to:** `chisel-results/TIMESTAMP/profile_summary.txt`

All examples include:
- **Kernel Performance**: Execution times, occupancy, and throughput analysis
- **Memory Analysis**: Bandwidth utilization and transfer patterns
- **API Timing**: CUDA/HIP/OpenCL API call breakdowns  
- **Optimization Insights**: Automated suggestions for performance improvements

## GPU Support

| GPU         | Size                | Region | Cost/Hour | Profiling                       |
| ----------- | ------------------- | ------ | --------- | ------------------------------- |
| NVIDIA H100 | `gpu-h100x1-80gb`   | NYC2   | $3.39     | nsight-compute + nsight-systems |
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

