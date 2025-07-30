"""
Adapters for various embedding models.

This module provides adapter classes for various embedding models to be used
with the SemanticDictionary class.
"""

from abc import ABC, abstractmethod
from typing import List, Union

import numpy as np
import torch
from transformers.modeling_outputs import BaseModelOutputWithPoolingAndCrossAttentions


class EmbeddingModelAdapter(ABC):
    """
    Abstract base class for embedding model adapters.

    Implement this class to create adapters for specific embedding models.
    """

    @abstractmethod
    def encode(self, text: str) -> np.ndarray:
        """
        Encode a text string into an embedding vector.

        Args:
            text: The text to encode

        Returns:
            A numpy array representing the embedding vector
        """
        pass


class SentenceTransformerAdapter(EmbeddingModelAdapter):
    """
    Adapter for sentence-transformers models.

    This adapter wraps a sentence-transformers model to be used with SemanticDictionary.
    """

    def __init__(self, model):
        """
        Initialize a new SentenceTransformerAdapter.

        Args:
            model: A sentence-transformers model instance
        """
        self.model = model

    def encode(self, text: str) -> np.ndarray:
        """
        Encode a text string into an embedding vector using sentence-transformers.

        Args:
            text: The text to encode

        Returns:
            A numpy array representing the embedding vector
        """
        return self.model.encode(text)


class HuggingFaceAdapter(EmbeddingModelAdapter):
    """
    Adapter for Hugging Face transformer models.

    This adapter wraps a Hugging Face model to be used with SemanticDictionary.
    """

    def __init__(self, tokenizer, model, pooling_strategy: str = "mean"):
        """
        Initialize a new HuggingFaceAdapter.

        Args:
            tokenizer: A Hugging Face tokenizer
            model: A Hugging Face model
            pooling_strategy: The pooling strategy to use ('mean', 'max', or 'cls')
        """
        self.tokenizer = tokenizer
        self.model = model
        self.pooling_strategy = pooling_strategy

    def encode(self, text: str) -> np.ndarray:
        """
        Encode a text string into an embedding vector using a Hugging Face model.

        Args:
            text: The text to encode

        Returns:
            A numpy array representing the embedding vector
        """
        # Tokenize the text
        inputs = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True
        )

        # Get the model outputs
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Apply pooling strategy based on model output type
        if (
            isinstance(outputs, BaseModelOutputWithPoolingAndCrossAttentions)
            and hasattr(outputs, "pooler_output")
            and self.pooling_strategy == "cls"
        ):
            # Use the model's built-in pooler if available (for BERT-like models)
            embeddings = outputs.pooler_output
        else:
            # Get the hidden states
            hidden_states = outputs.last_hidden_state

            # Apply pooling strategy
            if self.pooling_strategy == "mean":
                # Mean pooling - use attention mask for proper averaging
                attention_mask = inputs["attention_mask"].unsqueeze(-1)
                embeddings = torch.sum(hidden_states * attention_mask, 1) / torch.clamp(
                    attention_mask.sum(1), min=1e-9
                )
            elif self.pooling_strategy == "max":
                # Max pooling - mask out padding tokens with large negative value
                attention_mask = (
                    inputs["attention_mask"].unsqueeze(-1).expand_as(hidden_states)
                )
                # Create a copy to avoid modifying the original
                masked_states = hidden_states.clone()
                masked_states[attention_mask == 0] = -1e9
                embeddings = torch.max(masked_states, 1)[0]
            elif self.pooling_strategy == "cls":
                # CLS token
                embeddings = hidden_states[:, 0]
            else:
                raise ValueError(f"Unknown pooling strategy: {self.pooling_strategy}")

        return embeddings.cpu().numpy()[0]


class OpenAIAdapter(EmbeddingModelAdapter):
    """
    Adapter for OpenAI embedding models.

    This adapter wraps the OpenAI API to be used with SemanticDictionary.
    """

    def __init__(self, client, model: str = "text-embedding-3-small"):
        """
        Initialize a new OpenAIAdapter.

        Args:
            client: An OpenAI client instance
            model: The name of the OpenAI embedding model to use
        """
        self.client = client
        self.model = model

    def encode(self, text: str) -> np.ndarray:
        """
        Encode a text string into an embedding vector using OpenAI API.

        Args:
            text: The text to encode

        Returns:
            A numpy array representing the embedding vector
        """
        response = self.client.embeddings.create(model=self.model, input=text)

        return np.array(response.data[0].embedding)


class DummyEmbeddingModel(EmbeddingModelAdapter):
    """
    A dummy embedding model for testing purposes.

    This model returns random embeddings of a fixed dimension.
    """

    def __init__(self, dimension: int = 768, seed: int = None):
        """
        Initialize a new DummyEmbeddingModel.

        Args:
            dimension: The dimension of the embedding vectors
            seed: Random seed for reproducibility
        """
        self.dimension = dimension
        self.rng = np.random.RandomState(seed)
        self.cache = {}

    def encode(self, text: str) -> np.ndarray:
        """
        Encode a text string into a random embedding vector.

        Args:
            text: The text to encode

        Returns:
            A numpy array representing the embedding vector
        """
        # Cache embeddings for the same text
        if text not in self.cache:
            self.cache[text] = self.rng.randn(self.dimension)
            # Normalize the vector
            self.cache[text] = self.cache[text] / np.linalg.norm(self.cache[text])

        return self.cache[text]
