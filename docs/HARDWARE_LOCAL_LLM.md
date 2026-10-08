# Hardware Profiles & Local LLM Integration Guide

This build of Casper C2 Agent supports optimized local LLM and Google ADK execution across Casper's primary hardware profiles: **MacBook Neo** and **Alienware x17 R2**.

## Supported Hardware Specifications

### 1. MacBook Neo
- **Platform**: macOS (Apple Silicon ARM64)
- **Hardware Acceleration**: Metal Performance Shaders (MPS) / MLX framework
- **Memory**: Unified Memory architecture
- **Recommended Local LLMs**: `llama3:8b`, `gemma2:9b`, `mistral:7b`
- **Environment Configuration**:
  ```bash
  export OLLAMA_NUM_PARALLEL=2
  export OLLAMA_MAX_LOADED_MODELS=1
  ollama run llama3:8b
  ```
- **ADK / Vector Store Integration**: PyTorch automatically utilizes `mps` device acceleration for sentence transformer embeddings and local ADK agent tool calls.

### 2. Alienware x17 R2
- **Platform**: Windows / Linux (x86_64)
- **Hardware Acceleration**: NVIDIA GeForce RTX 3080 Ti (16GB VRAM) via CUDA & Tensor Cores
- **Processor**: Intel Core i7/i9
- **Recommended Local LLMs**: `llama3:70b-quant`, `gemma2:27b`, `codellama:34b`, `mistral:7b`
- **Environment Configuration**:
  ```bash
  export CUDA_VISIBLE_DEVICES=0
  export OLLAMA_NUM_PARALLEL=4
  export OLLAMA_MAX_LOADED_MODELS=2
  ollama run gemma2:27b
  ```
- **ADK / Vector Store Integration**: PyTorch automatically detects CUDA for ultra-fast SentenceTransformer embeddings and parallel local LLM worker execution via local endpoints (`http://localhost:11434`).

## Configuring Hardware Optimization via Agent Tool

The `Dev_Agent` includes the `get_hardware_optimization_config` tool, allowing you to generate hardware-tuned parameters dynamically:

```python
from skills.hardware_skills import get_hardware_optimization_config
from skills.models import HardwareConfigSchema

# For MacBook Neo
mac_config = get_hardware_optimization_config(
    HardwareConfigSchema(target_hardware="MacBook Neo", local_model_name="gemma2:9b")
)

# For Alienware x17 R2
alienware_config = get_hardware_optimization_config(
    HardwareConfigSchema(target_hardware="Alienware x17 R2", local_model_name="llama3:70b-quant")
)
```

## Vector Store Device Auto-Detection

The RAG engine (`memory/vector_tools.py`) detects hardware capabilities at runtime:
1. Checks for CUDA support (`torch.cuda.is_available()`) -> uses `"cuda"` device.
2. Checks for Apple Silicon MPS support (`torch.backends.mps.is_available()`) -> uses `"mps"` device.
3. Fallback to `"cpu"` if hardware accelerators are unavailable.
