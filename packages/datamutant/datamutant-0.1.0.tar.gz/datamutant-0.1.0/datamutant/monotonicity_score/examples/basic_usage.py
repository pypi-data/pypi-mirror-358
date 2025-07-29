#!/usr/bin/env python3
"""
Basic usage examples for sublinear monotonicity score algorithm.
"""

import torch
from datamutant.monotonicity_score import sublinear_monotonicity_score, generate_test_sequences, EnhancedModel


def basic_score_calculation():
    """Demonstrate basic monotonicity score calculation."""
    print("=== Basic Score Calculation ===")
    
    # Simple score calculation
    sequence = torch.tensor([1.0, 2.0, 3.0, 2.5, 4.0])
    score = sublinear_monotonicity_score(sequence, epsilon=0.1)
    print(f"Sublinear monotonicity score: {score:.3f}")
    
    # Get detailed statistics
    score, details = sublinear_monotonicity_score(sequence, epsilon=0.1, return_details=True)
    print(f"Score with details: {score:.3f}")
    print(f"Details: {details}")
    print()


def test_different_sequences():
    """Test different types of sequences."""
    print("=== Different Sequence Types ===")
    
    sequences = {
        "Perfect monotonic": torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0]),
        "Reverse monotonic": torch.tensor([5.0, 4.0, 3.0, 2.0, 1.0]),
        "Partially monotonic": torch.tensor([1.0, 2.0, 3.0, 2.5, 4.0, 5.0]),
        "Random": torch.tensor([3.0, 1.0, 4.0, 2.0, 5.0]),
        "Constant": torch.tensor([2.0, 2.0, 2.0, 2.0, 2.0]),
        "Noisy monotonic": torch.arange(10, dtype=torch.float32) + torch.randn(10) * 0.1
    }
    
    for name, seq in sequences.items():
        score = sublinear_monotonicity_score(seq, epsilon=0.1, seed=42)
        print(f"{name}: {score:.3f}")
    print()


def generate_and_test_sequences():
    """Generate test sequences and analyze them."""
    print("=== Generated Test Sequences ===")
    
    # Generate various test sequences
    sequences = generate_test_sequences(n=1000, seed=42)
    
    for name, seq in sequences.items():
        score = sublinear_monotonicity_score(seq)
        print(f"{name}: {score:.3f}")
    print()


def neural_network_integration():
    """Demonstrate integration with neural network models."""
    print("=== Neural Network Integration ===")
    
    # Create sample data
    batch_size = 16
    input_dim = 20
    data = torch.randn(batch_size, input_dim)
    
    # Calculate monotonicity scores for each sample
    scores = []
    for i in range(batch_size):
        score = sublinear_monotonicity_score(data[i], epsilon=0.1, seed=42)
        scores.append(score)
    
    mono_scores = torch.tensor(scores)
    print(f"Monotonicity scores shape: {mono_scores.shape}")
    print(f"Score range: [{mono_scores.min():.3f}, {mono_scores.max():.3f}]")
    
    # Use with EnhancedModel
    model = EnhancedModel(input_dim=input_dim, hidden_dims=[64, 32])
    output = model(data, mono_scores)
    print(f"Model output shape: {output.shape}")
    print()


def reproducibility_demo():
    """Demonstrate reproducibility with seeds."""
    print("=== Reproducibility Demo ===")
    
    sequence = torch.randn(1000) + torch.arange(1000, dtype=torch.float32) * 0.01
    
    # Same seed should give same results
    score1 = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=42)
    score2 = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=42)
    print(f"Same seed (42): {score1:.6f} == {score2:.6f}")
    
    # Different seeds might give slightly different results
    score3 = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=123)
    print(f"Different seed (123): {score3:.6f}")
    print()


def epsilon_comparison():
    """Compare different epsilon values."""
    print("=== Epsilon Comparison ===")
    
    # Create a large noisy monotonic sequence
    sequence = torch.arange(10000, dtype=torch.float32) + torch.randn(10000) * 0.1
    
    epsilons = [0.01, 0.05, 0.1, 0.2, 0.5]
    
    for eps in epsilons:
        score, details = sublinear_monotonicity_score(
            sequence, epsilon=eps, seed=42, return_details=True
        )
        samples = details['samples_taken']
        theoretical = details['theoretical_samples']
        print(f"ε={eps:4.2f}: score={score:.4f}, samples={samples:5d}, theoretical={theoretical:5d}")
    print()


if __name__ == "__main__":
    basic_score_calculation()
    test_different_sequences()
    generate_and_test_sequences()
    neural_network_integration()
    reproducibility_demo()
    epsilon_comparison()
    
    print("All examples completed successfully!") 