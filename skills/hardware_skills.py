import logging
from typing import Dict, Any
from skills.models import HardwareConfigSchema

logger = logging.getLogger("CasperC2.HardwareSkills")

HARDWARE_PROFILES = {
    "MacBook Neo": {
        "hardware_name": "MacBook Neo",
        "platform": "macOS",
        "architecture": "arm64 (Apple Silicon)",
        "acceleration": "Metal Performance Shaders (MPS) / MLX",
        "recommended_models": ["llama3:8b", "gemma2:9b", "mistral:7b"],
        "max_context_window": 8192,
        "ollama_env": {
            "OLLAMA_NUM_PARALLEL": "2",
            "OLLAMA_MAX_LOADED_MODELS": "1"
        },
        "adk_integration": "Supports local Ollama endpoint serving ADK LlmAgent sub-workers or local vector indexing via PyTorch MPS."
    },
    "Alienware x17 R2": {
        "hardware_name": "Alienware x17 R2",
        "platform": "Windows / Linux",
        "architecture": "x86_64",
        "gpu": "NVIDIA GeForce RTX 3080 Ti (16GB VRAM)",
        "acceleration": "NVIDIA CUDA / Tensor Cores",
        "recommended_models": ["llama3:70b-quant", "gemma2:27b", "codellama:34b", "mistral:7b"],
        "max_context_window": 16384,
        "ollama_env": {
            "OLLAMA_NUM_PARALLEL": "4",
            "OLLAMA_MAX_LOADED_MODELS": "2",
            "CUDA_VISIBLE_DEVICES": "0"
        },
        "adk_integration": "Supports heavy concurrent local LLM worker execution via Ollama/vLLM with CUDA acceleration and FAISS GPU indexing."
    }
}

def get_hardware_optimization_config(config: HardwareConfigSchema) -> Dict[str, Any]:
    """
    Returns optimal local LLM and Google ADK agent configuration parameters for Casper's target hardware (MacBook Neo or Alienware x17 R2).
    """
    target = config.target_hardware
    profile_key = "MacBook Neo"
    if "alienware" in target.lower() or "x17" in target.lower():
        profile_key = "Alienware x17 R2"

    profile = HARDWARE_PROFILES[profile_key].copy()
    endpoint = config.ollama_endpoint or "http://localhost:11434"
    selected_model = config.local_model_name or profile["recommended_models"][0]

    logger.info(f"Generated hardware optimization config for target: '{profile_key}' using model: '{selected_model}'")

    return {
        "target_hardware": profile_key,
        "specifications": profile,
        "configured_endpoint": endpoint,
        "configured_model": selected_model,
        "status": f"Hardware optimization profile configured for {profile_key}."
    }
