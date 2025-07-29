#!/usr/bin/env python3
"""
Model training example for sublinear monotonicity score algorithm.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from datamutant.monotonicity_score import EnhancedModel, sublinear_monotonicity_score, generate_test_sequences, MonotonicityPredictor


def generate_training_data(num_samples=1000, sequence_length=50):
    """Generate training data with monotonicity scores."""
    print(f"Generating {num_samples} training samples...")
    
    # Generate diverse sequences
    sequences = []
    labels = []
    
    for i in range(num_samples):
        if i % 4 == 0:
            # Monotonic sequences
            seq = torch.sort(torch.randn(sequence_length))[0]
            label = 1.0
        elif i % 4 == 1:
            # Reverse monotonic
            seq = torch.sort(torch.randn(sequence_length), descending=True)[0]
            label = 0.0
        elif i % 4 == 2:
            # Noisy monotonic
            base = torch.arange(sequence_length, dtype=torch.float32)
            noise = torch.randn(sequence_length) * 0.2
            seq = base + noise
            label = 0.8
        else:
            # Random
            seq = torch.randn(sequence_length)
            label = 0.5
        
        sequences.append(seq)
        labels.append(label)
    
    return torch.stack(sequences), torch.tensor(labels)


def train_enhanced_model():
    """Train an EnhancedModel to use monotonicity features."""
    print("=== Training Enhanced Model ===")
    
    # Generate training data
    X, y = generate_training_data(num_samples=1000, sequence_length=20)
    
    # Calculate monotonicity scores for features
    mono_scores = []
    for i in range(X.shape[0]):
        score = sublinear_monotonicity_score(X[i], epsilon=0.1, seed=42)
        mono_scores.append(score)
    mono_scores = torch.tensor(mono_scores)
    
    # Create model
    model = EnhancedModel(
        input_dim=20,
        hidden_dims=[64, 32],
        dropout_rate=0.3,
        use_monotonicity_features=True
    )
    
    # Setup training
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    num_epochs = 50
    batch_size = 32
    
    dataset = TensorDataset(X, mono_scores, y.unsqueeze(1))
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    for epoch in range(num_epochs):
        total_loss = 0
        for batch_x, batch_mono, batch_y in dataloader:
            optimizer.zero_grad()
            
            outputs = model(batch_x, batch_mono)
            loss = criterion(outputs, batch_y)
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            avg_loss = total_loss / len(dataloader)
            print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")
    
    # Test the model
    with torch.no_grad():
        test_outputs = model(X[:10], mono_scores[:10])
        print(f"Sample predictions: {test_outputs.flatten()[:5]}")
        print(f"Sample targets: {y[:5]}")
    
    print()


def train_monotonicity_predictor():
    """Train a MonotonicityPredictor to learn monotonicity from sequences."""
    print("=== Training Monotonicity Predictor ===")
    
    # Generate training data
    X, _ = generate_training_data(num_samples=1000, sequence_length=50)
    
    # Calculate true monotonicity scores as targets
    y = []
    for i in range(X.shape[0]):
        score = sublinear_monotonicity_score(X[i], epsilon=0.05, seed=42)
        y.append(score)
    y = torch.tensor(y).unsqueeze(1)
    
    # Create model
    model = MonotonicityPredictor(
        sequence_length=50,
        hidden_dims=[128, 64, 32],
        dropout_rate=0.2
    )
    
    # Setup training
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    num_epochs = 100
    batch_size = 32
    
    dataset = TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    for epoch in range(num_epochs):
        total_loss = 0
        for batch_x, batch_y in dataloader:
            optimizer.zero_grad()
            
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch + 1) % 20 == 0:
            avg_loss = total_loss / len(dataloader)
            print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")
    
    # Evaluate the model
    model.eval()
    with torch.no_grad():
        test_sequences = X[:20]
        predicted_scores = model(test_sequences).flatten()
        true_scores = y[:20].flatten()
        
        print(f"Predicted vs True scores:")
        for i in range(5):
            print(f"  Predicted: {predicted_scores[i]:.3f}, True: {true_scores[i]:.3f}")
        
        # Calculate MAE
        mae = torch.mean(torch.abs(predicted_scores - true_scores))
        print(f"Mean Absolute Error: {mae:.4f}")
    
    print()


def compare_algorithms():
    """Compare sublinear algorithm with actual sequences."""
    print("=== Algorithm Comparison ===")
    
    # Generate test sequences
    sequences = generate_test_sequences(n=1000, seed=42)
    
    print("Sequence analysis:")
    for name, seq in sequences.items():
        # Calculate with different epsilon values
        score_precise = sublinear_monotonicity_score(seq, epsilon=0.01, seed=42)
        score_fast = sublinear_monotonicity_score(seq, epsilon=0.2, seed=42)
        
        _, details = sublinear_monotonicity_score(seq, epsilon=0.1, seed=42, return_details=True)
        samples = details['samples_taken']
        
        print(f"{name:20}: precise={score_precise:.3f}, fast={score_fast:.3f}, samples={samples}")
    
    print()


def performance_benchmark():
    """Benchmark performance on different sequence sizes."""
    print("=== Performance Benchmark ===")
    
    import time
    
    sizes = [100, 1000, 10000, 50000]
    epsilon = 0.1
    
    print(f"{'Size':>8} {'Time (ms)':>10} {'Samples':>8} {'Score':>8}")
    print("-" * 40)
    
    for n in sizes:
        # Generate test sequence
        sequence = torch.arange(n, dtype=torch.float32) + torch.randn(n) * 0.1
        
        # Time the computation
        start_time = time.time()
        score, details = sublinear_monotonicity_score(
            sequence, epsilon=epsilon, seed=42, return_details=True
        )
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        samples = details['samples_taken']
        
        print(f"{n:8d} {duration_ms:10.2f} {samples:8d} {score:8.3f}")
    
    print()


if __name__ == "__main__":
    train_enhanced_model()
    train_monotonicity_predictor()
    compare_algorithms()
    performance_benchmark()
    
    print("Model training examples completed successfully!") 