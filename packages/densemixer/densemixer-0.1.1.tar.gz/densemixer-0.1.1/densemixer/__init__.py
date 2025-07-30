"""
DenseMixer: Enhanced Mixture of Experts implementation with optimized router.
"""
import os
import logging

__version__ = "0.1.0"
logger = logging.getLogger(__name__)

# Configuration system
class Config:
    def __init__(self):
        # Global switch
        self.enabled = self._get_env_bool("DENSEMIXER_ENABLED", True)
        
        # Model-specific switches
        self.models = {
            "qwen3": self._get_env_bool("DENSEMIXER_QWEN3", True),
            "olmoe": self._get_env_bool("DENSEMIXER_OLMOE", True),
            "qwen2": self._get_env_bool("DENSEMIXER_QWEN2", True)
        }
    
    def _get_env_bool(self, name, default=True):
        """Get boolean from environment variable"""
        val = os.environ.get(name, str(default)).lower()
        return val in ("1", "true", "yes", "on", "t")
    
    def is_model_enabled(self, model_name):
        """Check if a specific model is enabled"""
        return self.enabled and self.models.get(model_name, False)

# Initialize configuration
config = Config()

# Apply patches if enabled
if config.enabled:
    from .patching import apply_patches
    patched_models = apply_patches(config)
    if patched_models:
        logger.info(f"DenseMixer applied to: {', '.join(patched_models)}")
    else:
        logger.info("DenseMixer enabled but no models were patched")
else:
    logger.info("DenseMixer disabled via DENSEMIXER_ENABLED environment variable")