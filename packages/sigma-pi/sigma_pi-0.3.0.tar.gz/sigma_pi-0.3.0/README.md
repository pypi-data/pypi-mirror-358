# ΣPI: Observe the Cognitive ability of Your AI Model

[![PyPI version](https://badge.fury.io/py/sigma-pi.svg)](https://badge.fury.io/py/sigma-pi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/dmf-archive/SigmaPI)

**ΣPI** is a lightweight, universal SDK to calculate Predictive Integrity (PI), a metric from the Integrated Predictive Workspace Theory (IPWT) of consciousness. It provides a powerful, real-time proxy for your model's "cognitive state" during training.

Stop just looking at `loss`. Start observing how your model _learns_.

## What is Predictive Integrity (PI)?

PI is a score (0 to 1) reflecting a model's internal world model integrity, derived from prediction error (Epsilon), model uncertainty (Tau), and global gradient norm (Surprise). High PI indicates healthy learning; a drop can signal issues like overfitting before loss metrics do.

### Why Use ΣPI?

- **Early Warning for Training Instability:** Detects subtle shifts in model "cognition" before loss metrics diverge.
- **Insight into OOD Impact:** Quantifies the "surprise" your model experiences when encountering out-of-distribution data.
- **Understanding Model Overfitting:** Reveals when your model's internal world becomes too rigid or too chaotic.
- **Quantifying Cognitive Load:** Provides a novel metric for the "effort" your model expends to integrate new information.

## Model Zoo & Experiments

The complete model zoo, experimental framework (PILR-S), and all associated results have been migrated to a dedicated repository: **[dmf-archive/PILF](https://github.com/dmf-archive/PILF)**.

This `SigmaPI` repository now contains only the core SDK for calculating Predictive Integrity. Please visit the `PILF` repository for all implementation examples, training scripts, and pre-trained models.

## Installation

`SigmaPI` requires `torch` to be installed. To avoid conflicts with your existing (e.g., GPU-specific) `torch` installation, it is not listed as a hard dependency.

Please ensure `torch` is installed in your environment. If you want to install it alongside this package, you can use the `[torch]` extra:

```bash
# If you already have torch installed
pip install sigma-pi

# To install with torch
pip install sigma-pi[torch]
```

## How to Use

The `sigma-pi` package provides the core `SigmaPI` monitor. Here is a basic integration example:

```python
import torch
from sigma_pi import SigmaPI

# 1. Initialize the SigmaPI monitor once outside your training loop
sigma_pi = SigmaPI(device='cuda' if torch.cuda.is_available() else 'cpu')

# 2. Inside your training/validation loop:
#    (Ensure you are in a `with torch.enable_grad():` block for validation)

# Calculate loss
loss_epsilon = loss_fn(logits, target)

# Compute gradients (this is crucial)
model.zero_grad()
loss_epsilon.backward(create_graph=True) # Use create_graph=True if you need to backprop through PI metrics

# Calculate PI metrics
pi_metrics = sigma_pi.calculate(
    model=model,
    loss_epsilon=loss_epsilon,
    logits=logits
)

print(f"PI: {pi_metrics['pi_score']:.4f}, Surprise: {pi_metrics['surprise']:.4f}")

# Don't forget to step your optimizer after calculating PI
optimizer.step()
```

### Using with Automatic Mixed Precision (AMP)

When using `torch.cuda.amp.GradScaler`, it's crucial to calculate PI _after_ unscaling the gradients but _before_ the optimizer step. This ensures `ΣPI` receives the correct, unscaled gradient values.

Here is the recommended integration pattern:

```python
import torch
from sigma_pi import SigmaPI
from torch.cuda.amp import autocast, GradScaler

# 1. Initialize the SigmaPI monitor and GradScaler
sigma_pi = SigmaPI(device='cuda')
scaler = GradScaler()

# 2. Inside your training loop
model.train()
optimizer.zero_grad()

with autocast():
    logits = model(inputs)
    loss_epsilon = loss_fn(logits, target)

# Scale loss and compute gradients
scaler.scale(loss_epsilon).backward()

# Unscale gradients before optimizer step and PI calculation
scaler.unscale_(optimizer)

# --> Best place to calculate PI <--
# Gradients are now unscaled and ready for analysis.
pi_metrics = sigma_pi.calculate(
    model=model,
    loss_epsilon=loss_epsilon,
    logits=logits
)
print(f"PI: {pi_metrics['pi_score']:.4f}, Surprise: {pi_metrics['surprise']:.4f}")

# Optimizer step and scaler update
scaler.step(optimizer)
scaler.update()
```

The returned `pi_metrics` dictionary contains:

- `pi_score`: The overall predictive integrity (0-1)
- `surprise`: Gradient norm indicating model adaptation
- `normalized_error`: Error scaled by model uncertainty
- `cognitive_cost`: Combined cost of error and surprise
- Additional component metrics for detailed analysis

## Further Reading

PI is a concept derived from the **Integrated Predictive Workspace Theory (IPWT)**, a computational theory of consciousness. To understand the deep theory behind this tool, please refer to <https://github.com/dmf-archive/IPWT>

## Citation

If you wish to cite this work, please use the following BibTeX entry:

```bibtex
@misc{sigma_pi,
  author       = {Rui, L.},
  title        = {{ΣPI: Observe the Cognitive ability of Your AI Model}},
  year         = {2025},
  publisher    = {GitHub},
  url          = {https://github.com/dmf-archive/SigmaPI}
}
```

## License

This project is licensed under the MIT License.
