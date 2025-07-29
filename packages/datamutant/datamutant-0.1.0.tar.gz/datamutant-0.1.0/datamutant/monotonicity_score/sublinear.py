"""
Sublinear Monotonicity Score Extractor

This module provides a sublinear monotonicity score for 1D sequences (e.g., time series or ordered features),
measuring how close they are to being monotonically increasing using a sublinear number of samples.
"""

import torch
import math
from typing import Optional, Union, Tuple, Dict, Any
import random


def sublinear_monotonicity_score(
    input_tensor: torch.Tensor,
    epsilon: float = 0.1,
    seed: Optional[int] = None,
    return_details: bool = False
) -> Union[float, Tuple[float, Dict[str, Any]]]:
    """
    Calculate the monotonicity score for a 1D sequence using a sublinear algorithm.
    
    This algorithm samples O((1/ε) log n) pairs instead of checking all O(n²) pairs,
    making it much faster for large sequences while maintaining accuracy within ε.
    
    Args:
        input_tensor: 1D PyTorch tensor representing the sequence
        epsilon: Error tolerance (0 < ε ≤ 1). Lower values mean more samples and higher accuracy
        seed: Optional random seed for reproducible results
        return_details: If True, returns additional statistics about the computation
        
    Returns:
        Score between 0 and 1, or tuple of (score, details_dict) if return_details=True
        
    Raises:
        ValueError: If input_tensor is not 1D or epsilon is not in valid range
    """
    if len(input_tensor.shape) != 1:
        raise ValueError("Input tensor must be 1D")
    
    if not (0 < epsilon <= 1):
        raise ValueError("Epsilon must be in range (0, 1]")
    
    n = len(input_tensor)
    if n <= 1:
        return (1.0, {"samples_taken": 0, "violations": 0}) if return_details else 1.0
    
    # Set random seed for reproducibility
    if seed is not None:
        torch.manual_seed(seed)
        random.seed(seed)
    
    # Calculate number of samples needed: O((1/ε) log n)
    num_samples = min(n * (n - 1) // 2, max(1, int((1 / epsilon) * math.log(n))))
    
    # Generate random pairs (i, j) where i < j
    violations = 0
    samples_taken = 0
    
    for _ in range(num_samples):
        # Sample uniformly random pair (i, j) with i < j
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, n - 1)
        
        # Check for monotonicity violation
        if input_tensor[i] > input_tensor[j]:
            violations += 1
        
        samples_taken += 1
    
    # Calculate monotonicity score
    violation_rate = violations / samples_taken if samples_taken > 0 else 0.0
    score = 1.0 - violation_rate
    
    if return_details:
        details = {
            "samples_taken": samples_taken,
            "violations": violations,
            "violation_rate": violation_rate,
            "epsilon": epsilon,
            "sequence_length": n,
            "theoretical_samples": int((1 / epsilon) * math.log(n)) if n > 1 else 0
        }
        return score, details
    
    return score


def generate_test_sequences(n: int = 1000, seed: Optional[int] = None) -> Dict[str, torch.Tensor]:
    """
    Generate various test sequences for monotonicity analysis.
    
    Args:
        n: Length of sequences to generate
        seed: Optional random seed for reproducible results
        
    Returns:
        Dictionary of sequence_name -> tensor pairs
    """
    if seed is not None:
        torch.manual_seed(seed)
        random.seed(seed)
    
    sequences = {}
    
    # Perfect monotonic sequence
    sequences["perfect_monotonic"] = torch.arange(n, dtype=torch.float32)
    
    # Reverse monotonic (worst case)
    sequences["reverse_monotonic"] = torch.arange(n, 0, -1, dtype=torch.float32)
    
    # Noisy monotonic
    base = torch.arange(n, dtype=torch.float32)
    noise = torch.randn(n) * 0.1
    sequences["noisy_monotonic"] = base + noise
    
    # Nearly monotonic with few violations
    nearly_mono = torch.arange(n, dtype=torch.float32)
    # Introduce 5% violations
    violation_indices = random.sample(range(n-1), max(1, n//20))
    for i in violation_indices:
        nearly_mono[i], nearly_mono[i+1] = nearly_mono[i+1], nearly_mono[i]
    sequences["nearly_monotonic"] = nearly_mono
    
    # Random sequence
    sequences["random"] = torch.randn(n)
    
    # Alternating sequence (many violations)
    alternating = torch.zeros(n)
    for i in range(n):
        alternating[i] = i if i % 2 == 0 else n - i
    sequences["alternating"] = alternating
    
    # Sigmoid-like (mostly monotonic)
    x = torch.linspace(-6, 6, n)
    sequences["sigmoid"] = torch.sigmoid(x)
    
    return sequences 