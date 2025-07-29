"""
DataMutant - A Python library for advanced data analysis algorithms
"""

from .monotonicity_score import sublinear_monotonicity_score, generate_test_sequences, EnhancedModel

__version__ = "0.1.0"
__author__ = "Oscar Goldman"

__all__ = [
    "sublinear_monotonicity_score",
    "generate_test_sequences", 
    "EnhancedModel",
]

# Available algorithms
ALGORITHMS = [
    "sublinear_monotonicity_score",
    # Add more algorithms here as they are implemented
] 