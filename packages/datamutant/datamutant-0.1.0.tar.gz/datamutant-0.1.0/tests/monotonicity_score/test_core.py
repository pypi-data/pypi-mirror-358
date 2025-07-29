"""
Tests for monotonicity score functionality.
"""

import pytest
import torch
import math
from datamutant.monotonicity_score import sublinear_monotonicity_score, generate_test_sequences


class TestSublinearMonotonicityScore:
    """Test cases for sublinear monotonicity score algorithm."""

    def test_perfect_monotonic_sequence(self):
        """Test perfectly monotonic sequence returns score of 1.0."""
        sequence = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        score = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=42)
        assert score == 1.0

    def test_reverse_monotonic_sequence(self):
        """Test reverse monotonic sequence returns score close to 0.0."""
        sequence = torch.tensor([5.0, 4.0, 3.0, 2.0, 1.0])
        score = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=42)
        assert score == 0.0

    def test_partially_monotonic_sequence(self):
        """Test partially monotonic sequence returns intermediate score."""
        sequence = torch.tensor([1.0, 2.0, 3.0, 2.5, 4.0])
        score = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=42)
        assert 0.0 < score < 1.0

    def test_single_element_sequence(self):
        """Test single element sequence returns score of 1.0."""
        sequence = torch.tensor([42.0])
        score = sublinear_monotonicity_score(sequence)
        assert score == 1.0

    def test_empty_sequence_edge_case(self):
        """Test empty sequence handling."""
        sequence = torch.tensor([])
        score = sublinear_monotonicity_score(sequence)
        assert score == 1.0

    def test_two_element_sequences(self):
        """Test two-element sequences."""
        # Monotonic
        seq1 = torch.tensor([1.0, 2.0])
        score1 = sublinear_monotonicity_score(seq1, seed=42)
        assert score1 == 1.0
        
        # Non-monotonic
        seq2 = torch.tensor([2.0, 1.0])
        score2 = sublinear_monotonicity_score(seq2, seed=42)
        assert score2 == 0.0

    def test_return_details(self):
        """Test detailed statistics return."""
        sequence = torch.tensor([1.0, 3.0, 2.0, 4.0, 5.0])
        score, details = sublinear_monotonicity_score(
            sequence, epsilon=0.1, seed=42, return_details=True
        )
        
        assert isinstance(score, float)
        assert isinstance(details, dict)
        assert "samples_taken" in details
        assert "violations" in details
        assert "violation_rate" in details
        assert "epsilon" in details
        assert "sequence_length" in details
        assert "theoretical_samples" in details
        
        assert details["epsilon"] == 0.1
        assert details["sequence_length"] == 5

    def test_epsilon_validation(self):
        """Test epsilon parameter validation."""
        sequence = torch.tensor([1.0, 2.0, 3.0])
        
        # Valid epsilon values
        sublinear_monotonicity_score(sequence, epsilon=0.1)
        sublinear_monotonicity_score(sequence, epsilon=1.0)
        sublinear_monotonicity_score(sequence, epsilon=0.001)
        
        # Invalid epsilon values
        with pytest.raises(ValueError):
            sublinear_monotonicity_score(sequence, epsilon=0.0)
        
        with pytest.raises(ValueError):
            sublinear_monotonicity_score(sequence, epsilon=1.1)
        
        with pytest.raises(ValueError):
            sublinear_monotonicity_score(sequence, epsilon=-0.1)

    def test_tensor_dimension_validation(self):
        """Test input tensor dimension validation."""
        # Valid 1D tensor
        tensor_1d = torch.tensor([1.0, 2.0, 3.0])
        sublinear_monotonicity_score(tensor_1d)
        
        # Invalid 2D tensor
        tensor_2d = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
        with pytest.raises(ValueError):
            sublinear_monotonicity_score(tensor_2d)
        
        # Invalid 0D tensor
        tensor_0d = torch.tensor(5.0)
        with pytest.raises(ValueError):
            sublinear_monotonicity_score(tensor_0d)

    def test_reproducibility_with_seed(self):
        """Test that results are reproducible with same seed."""
        sequence = torch.randn(100)
        
        score1 = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=42)
        score2 = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=42)
        
        assert score1 == score2

    def test_different_seeds_different_results(self):
        """Test that different seeds can produce different results for noisy data."""
        # Use a sequence where sampling might matter
        sequence = torch.randn(1000) + torch.arange(1000, dtype=torch.float32) * 0.1
        
        score1 = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=42)
        score2 = sublinear_monotonicity_score(sequence, epsilon=0.1, seed=123)
        
        # Scores might be different due to random sampling
        # But both should be reasonable (we don't assert exact inequality)
        assert 0.0 <= score1 <= 1.0
        assert 0.0 <= score2 <= 1.0


class TestGenerateTestSequences:
    """Test cases for test sequence generation."""

    def test_generate_test_sequences_basic(self):
        """Test basic test sequence generation."""
        sequences = generate_test_sequences(n=100, seed=42)
        
        assert isinstance(sequences, dict)
        assert len(sequences) > 0
        
        # Check that all sequences have correct length
        for name, seq in sequences.items():
            assert len(seq) == 100
            assert isinstance(seq, torch.Tensor)

    def test_generate_test_sequences_reproducibility(self):
        """Test that sequence generation is reproducible with same seed."""
        seq1 = generate_test_sequences(n=50, seed=42)
        seq2 = generate_test_sequences(n=50, seed=42)
        
        assert set(seq1.keys()) == set(seq2.keys())
        
        for name in seq1:
            assert torch.allclose(seq1[name], seq2[name])

    def test_sequence_properties(self):
        """Test properties of generated sequences."""
        sequences = generate_test_sequences(n=100, seed=42)
        
        # Perfect monotonic should have score 1.0
        perfect_score = sublinear_monotonicity_score(
            sequences["perfect_monotonic"], epsilon=0.01, seed=42
        )
        assert perfect_score == 1.0
        
        # Reverse monotonic should have score 0.0
        reverse_score = sublinear_monotonicity_score(
            sequences["reverse_monotonic"], epsilon=0.01, seed=42
        )
        assert reverse_score == 0.0


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_large_sequence(self):
        """Test with large sequence."""
        large_seq = torch.arange(10000, dtype=torch.float32)
        score = sublinear_monotonicity_score(large_seq, epsilon=0.1)
        assert score >= 0.95
    
    def test_constant_sequence(self):
        """Test sequence with all equal values."""
        constant_seq = torch.ones(100)
        score = sublinear_monotonicity_score(constant_seq)
        assert score == 1.0
    
    def test_nan_values(self):
        """Test behavior with NaN values."""
        nan_seq = torch.tensor([1.0, float('nan'), 3.0])
        # This should not crash, but behavior with NaN is undefined
        score = sublinear_monotonicity_score(nan_seq)
        assert 0 <= score <= 1 or math.isnan(score)
    
    def test_inf_values(self):
        """Test behavior with infinite values."""
        inf_seq = torch.tensor([1.0, float('inf'), 3.0])
        score = sublinear_monotonicity_score(inf_seq)
        assert 0 <= score <= 1 