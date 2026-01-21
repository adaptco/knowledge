"""
Normalization utilities.

- Text normalization (NFKC, whitespace, line endings)
- Embedding normalization (L2)
"""
import re
import unicodedata

import torch


def normalize_text(text: str) -> str:
    """
    Normalize text for deterministic processing.
    
    - Unicode: NFKC normalization
    - Whitespace: collapse runs to single space
    - Line endings: normalize to LF
    """
    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)
    
    # Normalize line endings to LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Collapse whitespace runs (preserve newlines)
    text = re.sub(r"[^\S\n]+", " ", text)
    
    # Collapse multiple newlines to double newline (paragraph boundary)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()


def l2_normalize(x: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    """
    L2 normalize a tensor along the last dimension.
    
    Args:
        x: Input tensor of shape (..., dim)
        eps: Small epsilon to prevent division by zero
        
    Returns:
        L2-normalized tensor
    """
    norm = torch.norm(x, p=2, dim=-1, keepdim=True)
    return x / torch.clamp(norm, min=eps)


def l2_normalize_numpy(x):
    """
    L2 normalize a numpy array.
    
    Args:
        x: Input array of shape (..., dim)
        
    Returns:
        L2-normalized array
    """
    import numpy as np
    norm = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.maximum(norm, 1e-12)
