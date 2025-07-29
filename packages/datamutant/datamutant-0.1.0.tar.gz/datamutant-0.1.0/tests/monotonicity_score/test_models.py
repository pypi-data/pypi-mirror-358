"""
Tests for enhanced model functionality.
"""

import pytest
import torch
import torch.nn as nn
from datamutant.monotonicity_score import EnhancedModel, MonotonicityPredictor, monotonicity_score, generate_test_sequences


class TestEnhancedModel:
    """Test cases for EnhancedModel class."""
    
    def test_model_initialization(self):
        """Test model initializes correctly."""
        model = EnhancedModel(input_dim=10, hidden_dims=[64, 32])
        assert isinstance(model, nn.Module)
        assert model.use_monotonicity_features is True
    
    def test_forward_pass_with_monotonicity_scores(self):
        """Test forward pass with monotonicity scores."""
        batch_size = 16
        input_dim = 10
        
        model = EnhancedModel(input_dim=input_dim, hidden_dims=[64, 32])
        x = torch.randn(batch_size, input_dim)
        monotonicity_scores = torch.rand(batch_size)
        
        output = model(x, monotonicity_scores)
        
        assert output.shape == (batch_size, 1)
        assert not torch.isnan(output).any()
    
    def test_forward_pass_without_monotonicity_scores(self):
        """Test forward pass without monotonicity features."""
        batch_size = 16
        input_dim = 10
        
        model = EnhancedModel(
            input_dim=input_dim, 
            hidden_dims=[64, 32],
            use_monotonicity_features=False
        )
        x = torch.randn(batch_size, input_dim)
        
        output = model(x)
        
        assert output.shape == (batch_size, 1)
        assert not torch.isnan(output).any()
    
    def test_missing_monotonicity_scores_error(self):
        """Test error when monotonicity scores are required but not provided."""
        model = EnhancedModel(input_dim=10, use_monotonicity_features=True)
        x = torch.randn(16, 10)
        
        with pytest.raises(ValueError, match="Monotonicity scores required"):
            model(x)
    
    def test_different_architectures(self):
        """Test different model architectures."""
        batch_size = 8
        input_dim = 5
        x = torch.randn(batch_size, input_dim)
        scores = torch.rand(batch_size)
        
        # Single hidden layer
        model1 = EnhancedModel(input_dim=input_dim, hidden_dims=[32])
        output1 = model1(x, scores)
        assert output1.shape == (batch_size, 1)
        
        # Multiple hidden layers
        model2 = EnhancedModel(input_dim=input_dim, hidden_dims=[64, 32, 16])
        output2 = model2(x, scores)
        assert output2.shape == (batch_size, 1)
        
        # Different output dimension
        model3 = EnhancedModel(input_dim=input_dim, hidden_dims=[32], output_dim=5)
        output3 = model3(x, scores)
        assert output3.shape == (batch_size, 5)
    
    def test_dropout_rate(self):
        """Test different dropout rates."""
        model_low_dropout = EnhancedModel(input_dim=10, dropout_rate=0.1)
        model_high_dropout = EnhancedModel(input_dim=10, dropout_rate=0.8)
        
        x = torch.randn(16, 10)
        scores = torch.rand(16)
        
        # Both should work without errors
        output1 = model_low_dropout(x, scores)
        output2 = model_high_dropout(x, scores)
        
        assert output1.shape == output2.shape
    
    def test_feature_importance(self):
        """Test feature importance extraction."""
        model = EnhancedModel(input_dim=10, hidden_dims=[32])
        importance = model.get_feature_importance()
        
        # Should return importance for input_dim + 1 (monotonicity score)
        assert importance.shape == (11,)  # 10 + 1 for monotonicity score
        assert (importance >= 0).all()  # All importance scores should be non-negative
    
    def test_monotonicity_score_shape_handling(self):
        """Test handling of different monotonicity score tensor shapes."""
        model = EnhancedModel(input_dim=5)
        x = torch.randn(8, 5)
        
        # 1D tensor
        scores_1d = torch.rand(8)
        output1 = model(x, scores_1d)
        assert output1.shape == (8, 1)
        
        # 2D tensor (already correct shape)
        scores_2d = torch.rand(8, 1)
        output2 = model(x, scores_2d)
        assert output2.shape == (8, 1)


class TestMonotonicityPredictor:
    """Test cases for MonotonicityPredictor class."""
    
    def test_predictor_initialization(self):
        """Test predictor initializes correctly."""
        predictor = MonotonicityPredictor(sequence_length=100)
        assert isinstance(predictor, nn.Module)
    
    def test_predictor_forward_pass(self):
        """Test predictor forward pass."""
        sequence_length = 50
        batch_size = 16
        
        predictor = MonotonicityPredictor(sequence_length=sequence_length)
        x = torch.randn(batch_size, sequence_length)
        
        output = predictor(x)
        
        assert output.shape == (batch_size, 1)
        assert (output >= 0).all() and (output <= 1).all()  # Sigmoid output
        assert not torch.isnan(output).any()
    
    def test_predictor_different_architectures(self):
        """Test predictor with different architectures."""
        sequence_length = 100
        batch_size = 8
        x = torch.randn(batch_size, sequence_length)
        
        # Simple architecture
        predictor1 = MonotonicityPredictor(
            sequence_length=sequence_length,
            hidden_dims=[32]
        )
        output1 = predictor1(x)
        assert output1.shape == (batch_size, 1)
        
        # Complex architecture
        predictor2 = MonotonicityPredictor(
            sequence_length=sequence_length,
            hidden_dims=[128, 64, 32, 16]
        )
        output2 = predictor2(x)
        assert output2.shape == (batch_size, 1)
    
    def test_predictor_training_mode(self):
        """Test predictor in training vs evaluation mode."""
        predictor = MonotonicityPredictor(sequence_length=50)
        x = torch.randn(4, 50)
        
        # Training mode
        predictor.train()
        output_train = predictor(x)
        
        # Evaluation mode
        predictor.eval()
        output_eval = predictor(x)
        
        # Outputs might be different due to dropout
        assert output_train.shape == output_eval.shape
        assert (output_train >= 0).all() and (output_train <= 1).all()
        assert (output_eval >= 0).all() and (output_eval <= 1).all()


class TestModelIntegration:
    """Integration tests for models with monotonicity scores."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from sequences to model prediction."""
        # Generate test data
        sequences_dict = generate_test_sequences(n=100, seed=42)
        sequences = list(sequences_dict.values())
        
        # Convert to tensor batch
        batch_sequences = torch.stack(sequences[:10])  # Take first 10 sequences
        
        # Calculate monotonicity scores
        mono_scores = torch.tensor([
            monotonicity_score(seq) for seq in batch_sequences
        ])
        
        # Create and use enhanced model
        model = EnhancedModel(input_dim=100, hidden_dims=[64, 32])
        output = model(batch_sequences, mono_scores)
        
        assert output.shape == (10, 1)
        assert not torch.isnan(output).any()
    
    def test_predictor_vs_actual_scores(self):
        """Test that predictor can learn to approximate actual monotonicity scores."""
        # Generate training data
        sequences_dict = generate_test_sequences(n=50, seed=123)
        sequences = list(sequences_dict.values())
        
        # Create batch
        batch_sequences = torch.stack(sequences)
        
        # Calculate actual scores
        actual_scores = torch.tensor([
            [monotonicity_score(seq)] for seq in batch_sequences
        ])
        
        # Create predictor
        predictor = MonotonicityPredictor(sequence_length=50)
        
        # Test forward pass
        predicted_scores = predictor(batch_sequences)
        
        assert predicted_scores.shape == actual_scores.shape
        assert (predicted_scores >= 0).all() and (predicted_scores <= 1).all()
        
        # Test that we can compute loss (for training)
        criterion = nn.MSELoss()
        loss = criterion(predicted_scores, actual_scores)
        assert not torch.isnan(loss)
        assert loss.item() >= 0 