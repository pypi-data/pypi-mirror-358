"""
Semantic Dictionary - A dictionary-like class that uses semantic similarity for key matching.

This package provides a dictionary-like class that uses semantic similarity
for key matching instead of exact matches.
"""

from .adapters import (
    DummyEmbeddingModel,
    EmbeddingModelAdapter,
    HuggingFaceAdapter,
    OpenAIAdapter,
    SentenceTransformerAdapter,
)
from .semantic_dictionary import (
    EmbeddingError,
    SemanticDictionary,
    ZeroVectorError,
)

__all__ = [
    "SemanticDictionary",
    "EmbeddingModelAdapter",
    "SentenceTransformerAdapter",
    "HuggingFaceAdapter",
    "OpenAIAdapter",
    "DummyEmbeddingModel",
    "ZeroVectorError",
    "EmbeddingError",
]
__version__ = "0.1.0"
