# DenseMixer

Enhanced Mixture of Experts implementation with optimized router for multiple MoE models.

## Supported Models

- Qwen3-MoE
- Qwen2-MoE
- OLMoE

## Installation

```bash
pip install densemixer
```

## Usage: Auto-Patching Setup (No Manual Import Needed)

To enable DenseMixer automatically for all Python scripts (without needing to add any import):

```bash
densemixer setup
export DENSEMIXER_ENABLED=1
```

This will append the necessary auto-import logic to your `usercustomize.py` in your user site-packages (if not already present). Any Python process with `DENSEMIXER_ENABLED=1` will auto-load DenseMixer and patch transformers models.

To disable, either unset the environment variable or manually remove the relevant lines from your `usercustomize.py` in your user site-packages.

## Example

```python
from transformers import Qwen3MoeForCausalLM

model = Qwen3MoeForCausalLM.from_pretrained("Qwen/Qwen3-MoE-15B-A2B")
```

## Configuration

DenseMixer can be controlled with environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DENSEMIXER_ENABLED` | `1` | Master switch to enable/disable DenseMixer |
| `DENSEMIXER_QWEN3` | `1` | Enable for Qwen3-MoE models |
| `DENSEMIXER_QWEN2` | `1` | Enable for Qwen2-MoE models |
| `DENSEMIXER_OLMOE` | `1` | Enable for OLMoE models |

### Examples

Disable DenseMixer completely:
```bash
export DENSEMIXER_ENABLED=0
python your_script.py
```

Only enable for Qwen3-MoE:
```bash
export DENSEMIXER_ENABLED=1
export DENSEMIXER_QWEN3=1
export DENSEMIXER_QWEN2=0
export DENSEMIXER_OLMOE=0
python your_script.py
```