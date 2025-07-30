# PyTorch Gradient Reversal Layer

[![PyPI version](https://badge.fury.io/py/torch-gradient-reversal.svg)](https://badge.fury.io/py/torch-gradient-reversal)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Apparrently there are no graphable implementations of the famous DANN paper's Gradient Reversal Layer in Torch. This package implements the Gradient Reversal Layer (GRL) in PyTorch using the `torch.library` API. It is fully compatible with `torch.compile`, CUDA graphs, and distributed training as of Torch v2.7. I am releasing this so no one else will need to experience the pain and suffering to get this right; expect limited updates for future versions.

## Installation

### From PyPI (Recommended)
```bash
pip install torch-gradient-reversal
```

### From Source
```bash
git clone https://github.com/andrewbistras/torch-gradient-reversal.git
cd torch-gradient-reversal
pip install -e .
```

### Basic Usage

```python
import torch
from gradient_reversal import GradientReversalLayer

# Create a gradient reversal layer
grl = GradientReversalLayer(alpha=1.0)

# Use in a model
model = torch.nn.Sequential(
    torch.nn.Linear(10, 20),
    torch.nn.ReLU(),
    grl,  # Reverses gradients during backprop
    torch.nn.Linear(20, 2)
)

# Forward pass works normally
x = torch.randn(32, 10)
output = model(x)

# During backward pass, gradients are reversed and scaled by alpha
loss = output.sum()
loss.backward()
```

### Domain Adaptation Example

```python
import torch.nn as nn
from gradient_reversal import GradientReversalLayer

class DomainAdaptationModel(nn.Module):
    def __init__(self):
        super().__init__()
        
        # Shared feature extractor
        self.feature_extractor = nn.Sequential(
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Linear(256, 128)
        )
        
        # Task classifier (for main task)
        self.task_classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 10)  # 10 classes
        )
        
        # Domain classifier (with gradient reversal)
        self.domain_classifier = nn.Sequential(
            GradientReversalLayer(alpha=1.0),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 2)  # Binary: source/target
        )
    
    def forward(self, x):
        features = self.feature_extractor(x)
        task_output = self.task_classifier(features)
        domain_output = self.domain_classifier(features)
        return task_output, domain_output
```

### Dynamic Alpha Scheduling

```python
# Gradually increase gradient reversal strength during training
for epoch in range(num_epochs):
    # Schedule alpha from 0 to 1
    p = epoch / num_epochs
    alpha = 2 / (1 + np.exp(-10 * p)) - 1
    
    # Update the GRL alpha
    model.domain_classifier[0].set_alpha(alpha)
    
    # Training loop...
```

## How It Works

The Gradient Reversal Layer reverses and scales the backprop gradient as described in ["Unsupervised Domain Adaptation by Backpropagation"](https://arxiv.org/abs/1409.7495) by Ganin et al.

- **Forward Pass**: Acts as an identity function (output = input)
- **Backward Pass**: Reverses the gradient and scales by -alpha

This enables theoretically concurrent adversarial training with rich shared signals.


### Using with torch.compile

```python
import torch

# Model with GRL
model = create_model_with_grl()

# Compile the model for faster execution
compiled_model = torch.compile(model)

# Use as normal
output = compiled_model(input)
```


### Distributed Training

```python
# Works seamlessly with DDP
model = DomainAdaptationModel()
model = torch.nn.parallel.DistributedDataParallel(model)
```

## API Reference

### GradientReversalLayer

```python
class GradientReversalLayer(nn.Module):
    """Gradient Reversal Layer for domain adaptation.
    
    Args:
        alpha (float): Gradient scaling factor. Default: 1.0
    """
    
    def forward(self, x: Tensor) -> Tensor:
        """Forward pass (identity function)."""
        
    def set_alpha(self, alpha: float) -> None:
        """Update gradient scaling factor."""
```

### Functional Interface

```python
def gradient_reversal(x: Tensor, alpha: float = 1.0) -> Tensor:
    """Functional gradient reversal operation."""
```

## License

See the MIT [LICENSE](LICENSE) for details.
