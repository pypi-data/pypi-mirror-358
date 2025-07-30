"""
Logging utilities for DenseMixer package.
"""

import logging
from typing import Dict, Set

# Track which models have already logged their custom forward usage
_logged_models: Set[str] = set()

def log_custom_forward_usage(model_name: str, logger: logging.Logger = None) -> None:
    """
    Log that a custom forward method is being used for a specific model.
    This will only log once per model type to avoid spam.
    
    Args:
        model_name: Name of the model (e.g., "OLMoE", "Qwen2-MoE", "Qwen3-MoE")
        logger: Logger instance to use. If None, creates a default logger.
    """
    if model_name in _logged_models:
        return
    
    if logger is None:
        logger = logging.getLogger("densemixer")
    
    logger.info(f"DenseMixer: Using custom forward method for {model_name}")
    _logged_models.add(model_name)

def reset_logged_models() -> None:
    """
    Reset the logged models set. Useful for testing or if you want to re-log.
    """
    global _logged_models
    _logged_models.clear() 