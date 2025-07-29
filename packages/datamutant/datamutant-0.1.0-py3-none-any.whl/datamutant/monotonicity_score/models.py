"""
Enhanced Neural Network Models for Monotonicity Analysis

This module provides neural network models that can incorporate monotonicity scores
as features for downstream tasks.
"""

import torch
import torch.nn as nn
from typing import List, Optional


class EnhancedModel(nn.Module):
    """
    Enhanced neural network model with batch normalization and dropout.
    
    This model can process input features along with monotonicity scores
    for various machine learning tasks.
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int] = [64, 32],
        dropout_rate: float = 0.3,
        output_dim: int = 1,
        use_monotonicity_features: bool = True
    ):
        """
        Initialize the enhanced model.
        
        Args:
            input_dim: Dimension of input features
            hidden_dims: List of hidden layer dimensions
            dropout_rate: Dropout rate for regularization
            output_dim: Output dimension
            use_monotonicity_features: Whether to include monotonicity score as a feature
        """
        super(EnhancedModel, self).__init__()
        
        self.use_monotonicity_features = use_monotonicity_features
        
        # Adjust input dimension if using monotonicity features
        actual_input_dim = input_dim + 1 if use_monotonicity_features else input_dim
        
        # Build the network layers
        layers = []
        prev_dim = actual_input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
    
    def forward(self, x: torch.Tensor, monotonicity_scores: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass through the network.
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
            monotonicity_scores: Optional monotonicity scores of shape (batch_size,)
            
        Returns:
            Output tensor of shape (batch_size, output_dim)
        """
        if self.use_monotonicity_features:
            if monotonicity_scores is None:
                raise ValueError("Monotonicity scores required when use_monotonicity_features=True")
            
            # Ensure monotonicity_scores has the right shape
            if len(monotonicity_scores.shape) == 1:
                monotonicity_scores = monotonicity_scores.unsqueeze(1)
            
            # Concatenate input features with monotonicity scores
            x = torch.cat([x, monotonicity_scores], dim=1)
        
        return self.network(x)
    
    def get_feature_importance(self) -> torch.Tensor:
        """
        Get feature importance based on first layer weights.
        
        Returns:
            Tensor of feature importance scores
        """
        first_layer = self.network[0]  # First linear layer
        return torch.abs(first_layer.weight).mean(dim=0)


class MonotonicityPredictor(nn.Module):
    """
    A specialized model for predicting monotonicity scores from sequences.
    """
    
    def __init__(
        self,
        sequence_length: int,
        hidden_dims: List[int] = [128, 64, 32],
        dropout_rate: float = 0.2
    ):
        """
        Initialize the monotonicity predictor.
        
        Args:
            sequence_length: Expected length of input sequences
            hidden_dims: List of hidden layer dimensions
            dropout_rate: Dropout rate for regularization
        """
        super(MonotonicityPredictor, self).__init__()
        
        layers = []
        prev_dim = sequence_length
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        # Output layer with sigmoid activation for score in [0, 1]
        layers.extend([
            nn.Linear(prev_dim, 1),
            nn.Sigmoid()
        ])
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass to predict monotonicity score.
        
        Args:
            x: Input sequences of shape (batch_size, sequence_length)
            
        Returns:
            Predicted monotonicity scores of shape (batch_size, 1)
        """
        return self.network(x) 