"""
PyTorch Gradient Reversal Layer

A modern implementation of the Gradient Reversal Layer (GRL) using PyTorch's
torch.library API. This implementation provides full compatibility with:
- torch.compile() and TorchScript
- CUDA graphs and torch.jit.script
- Distributed training (DDP, FSDP)

Based on:
    Ganin, Y., & Lempitsky, V. (2015). Unsupervised domain adaptation by 
    backpropagation. In International conference on machine learning (pp. 1180-1189).
    
Author: Andrew Bistras
License: MIT
"""

import torch
from torch import Tensor
from torch.library import Library, impl, register_autograd
import torch.nn as nn
__all__ = ["GradientReversalLayer", "gradient_reversal"]


# Register the gradient reversal operation with PyTorch's dispatcher
_lib = Library("gradient_reversal", "DEF")
_lib.define("grl(Tensor x, float alpha) -> Tensor")


@impl(_lib, "grl", "CompositeExplicitAutograd")
def _gradient_reversal_forward(x: Tensor, alpha: float) -> Tensor:
    """
    Acts as an identity function in the forward pass.
    We use aten.alias for a zero-copy identity operation.
    """
    return torch.ops.aten.alias(x)


def _setup_context(ctx, inputs, output):
    """Save the gradient scaling factor for the backward pass."""
    _, alpha = inputs
    ctx.alpha = alpha


def _gradient_reversal_backward(ctx, grad_output: Tensor):
    """
    Scales the gradient by -alpha.
    """
    return -ctx.alpha * grad_output, None


# Register the autograd implementation
register_autograd(
    "gradient_reversal::grl", 
    _gradient_reversal_backward, 
    setup_context=_setup_context,
)


# Register fake kernel for torch.compile and meta tensors
@torch.library.register_fake("gradient_reversal::grl")
def _gradient_reversal_fake(x: Tensor, alpha: float) -> Tensor:
    """
    Fake kernel for shape/dtype/device propagation in torch.compile.
    
    This enables the operator to work with FakeTensor tracing used by
    torch.compile, torch.export, and other PyTorch compiler technologies.
    """
    return torch.ops.aten.alias(x)


def gradient_reversal(x: Tensor, alpha: float = 1.0) -> Tensor:
    """
    Applies gradient reversal to the input tensor.
    
    During the forward pass, this function acts as an identity operation.
    During the backward pass, it reverses the gradient and scales it by -alpha.
    
    This is commonly used in domain adaptation to train domain-invariant features.
    
    Args:
        x: Input tensor of any shape
        alpha: Gradient reversal strength. The gradient is multiplied by -alpha
               during backpropagation. Default: 1.0
               Common usage: gradually increase from 0 to 1 during training
    
    Returns:
        Output tensor (same as input during forward pass)
        
    Example:
        >>> # In a domain adaptation model
        >>> features = feature_extractor(x)
        >>> # Reverse gradients for domain classifier
        >>> domain_features = gradient_reversal(features, alpha=0.5)
        >>> domain_pred = domain_classifier(domain_features)
    """
    return torch.ops.gradient_reversal.grl(x, float(alpha))


class GradientReversalLayer(nn.Module):
    """
    Gradient Reversal Layer module for domain adaptation.
    
    This layer acts as an identity function during forward propagation but
    reverses and scales gradients during backpropagation. It's designed to
    be used in adversarial domain adaptation architectures where the goal
    is to learn domain-invariant features.
    
    The gradient reversal causes the feature extractor to learn representations
    that make it difficult for the domain classifier to distinguish between
    source and target domains.
    
    Args:
        alpha: Gradient reversal strength. The gradient is multiplied by -alpha
               during backpropagation. Default: 1.0
               
    Attributes:
        alpha: Buffer containing the gradient reversal strength
        
    Example:
        >>> # Building a DANN (Domain-Adversarial Neural Network)
        >>> model = nn.Sequential(
        ...     # Shared feature extractor
        ...     nn.Linear(input_dim, 128),
        ...     nn.ReLU(),
        ...     nn.Linear(128, 64),
        ...     nn.ReLU(),
        ... )
        ... 
        >>> # Task classifier branch
        >>> task_classifier = nn.Linear(64, num_classes)
        ... 
        >>> # Domain classifier branch with gradient reversal
        >>> domain_classifier = nn.Sequential(
        ...     GradientReversalLayer(alpha=lambda_value),
        ...     nn.Linear(64, 32),
        ...     nn.ReLU(),
        ...     nn.Linear(32, 2)  # Binary: source/target
        ... )
        
    Note:
        The alpha parameter is registered as a buffer, not a parameter,
        so it won't be updated by optimizers but will be saved/loaded
        with the model state.
    """
    
    def __init__(self, alpha: float = 1.0):
        super().__init__()
        # Register as buffer so it's included in state_dict but not optimized
        self.register_buffer("alpha", torch.tensor(float(alpha)))
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass - acts as identity function.
        
        Args:
            x: Input tensor of any shape
            
        Returns:
            Same tensor as input (identity operation)
        """
        return torch.ops.gradient_reversal.grl(x, float(self.alpha))
    
    def set_alpha(self, alpha: float) -> None:
        """
        Update the gradient reversal strength.
        
        This is useful for scheduling alpha during training, e.g., gradually
        increasing it from 0 to 1 to discourage adversarial collapse.
        
        Args:
            alpha: New gradient reversal strength
        """
        self.alpha.fill_(float(alpha))
    
    def extra_repr(self) -> str:
        """String representation for printing the module."""
        return f"alpha={float(self.alpha):.4f}"
