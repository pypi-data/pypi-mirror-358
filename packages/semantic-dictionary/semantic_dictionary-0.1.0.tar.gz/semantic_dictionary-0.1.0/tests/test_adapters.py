"""
Tests for the adapter classes in the semantic_dictionary package.
"""

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import torch
from transformers.modeling_outputs import BaseModelOutputWithPoolingAndCrossAttentions

from semantic_dictionary.adapters import (
    DummyEmbeddingModel,
    EmbeddingModelAdapter,
    HuggingFaceAdapter,
    OpenAIAdapter,
    SentenceTransformerAdapter,
)


class TestEmbeddingModelAdapter(unittest.TestCase):
    """Test cases for the abstract EmbeddingModelAdapter class."""

    def test_abstract_class(self):
        """Test that the abstract class cannot be instantiated."""
        with self.assertRaises(TypeError):
            EmbeddingModelAdapter()

    def test_abstract_encode_method(self):
        """Test the abstract encode method of EmbeddingModelAdapter."""

        # Create a concrete subclass of EmbeddingModelAdapter without implementing encode
        class ConcreteAdapter(EmbeddingModelAdapter):
            pass

        # Attempting to instantiate this class should raise TypeError
        with self.assertRaises(TypeError):
            adapter = ConcreteAdapter()


class TestSentenceTransformerAdapter(unittest.TestCase):
    """Test cases for the SentenceTransformerAdapter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model = MagicMock()
        self.mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        self.adapter = SentenceTransformerAdapter(self.mock_model)

    def test_encode(self):
        """Test that encode method calls the model's encode method."""
        result = self.adapter.encode("test text")

        # Check that the model's encode method was called with the correct text
        self.mock_model.encode.assert_called_once_with("test text")

        # Check that the result is the expected numpy array
        np.testing.assert_array_equal(result, np.array([0.1, 0.2, 0.3]))


class TestHuggingFaceAdapter(unittest.TestCase):
    """Test cases for the HuggingFaceAdapter class."""

    def setUp(self):
        """Set up test fixtures before each test."""
        # Mock the necessary components
        self.mock_tokenizer = MagicMock()
        self.mock_model = MagicMock()

    def test_encode_with_built_in_pooler(self):
        """Test encode method using the model's built-in pooler output."""
        # Create adapter with cls pooling strategy
        adapter = HuggingFaceAdapter(self.mock_tokenizer, self.mock_model, "cls")

        # Mock tokenizer output
        mock_inputs = {
            "attention_mask": torch.ones((1, 4)),
            "input_ids": torch.ones((1, 4)),
        }
        self.mock_tokenizer.return_value = mock_inputs

        # Mock the model's output to include a pooler_output
        mock_outputs = BaseModelOutputWithPoolingAndCrossAttentions(
            last_hidden_state=torch.tensor(
                [[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8]]]
            ),
            pooler_output=torch.tensor([[0.9, 1.0]]),
        )
        self.mock_model.return_value = mock_outputs

        with patch("torch.no_grad"):
            result = adapter.encode("test text")

            # Check that the result is the pooler_output
            np.testing.assert_array_equal(
                result, mock_outputs.pooler_output.cpu().numpy()[0]
            )

            # Check that the tokenizer and model were called correctly
            self.mock_tokenizer.assert_called_once()
            self.mock_model.assert_called_once()

    def test_encode_cls_without_built_in_pooler(self):
        """Test CLS pooling when the model doesn't have a built-in pooler."""
        # Create adapter with cls pooling strategy
        adapter = HuggingFaceAdapter(self.mock_tokenizer, self.mock_model, "cls")

        # Mock tokenizer output
        mock_inputs = {
            "attention_mask": torch.ones((1, 4)),
            "input_ids": torch.ones((1, 4)),
        }
        self.mock_tokenizer.return_value = mock_inputs

        # Mock the model's output without a pooler_output
        mock_outputs = MagicMock()
        mock_outputs.last_hidden_state = torch.tensor(
            [[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8]]]
        )
        # Ensure it's not recognized as having a pooler_output
        type(mock_outputs).__name__ = "BaseModelOutput"
        self.mock_model.return_value = mock_outputs

        with patch("torch.no_grad"):
            result = adapter.encode("test text")

            # Check that the result is the first token's embedding (CLS token)
            np.testing.assert_array_equal(
                result, mock_outputs.last_hidden_state[0, 0].cpu().numpy()
            )

    def test_encode_mean_pooling(self):
        """Test mean pooling strategy."""
        # Create adapter with mean pooling strategy
        adapter = HuggingFaceAdapter(self.mock_tokenizer, self.mock_model, "mean")

        # Mock tokenizer output with attention mask
        attention_mask = torch.tensor([[1, 1, 1, 0]])  # 3 tokens + 1 padding
        mock_inputs = {
            "attention_mask": attention_mask,
            "input_ids": torch.ones((1, 4)),
        }
        self.mock_tokenizer.return_value = mock_inputs

        # Create hidden states with recognizable values
        hidden_states = torch.tensor(
            [
                [  # Batch dimension
                    [1.0, 2.0],  # Token 1
                    [3.0, 4.0],  # Token 2
                    [5.0, 6.0],  # Token 3
                    [7.0, 8.0],  # Padding (should be masked)
                ]
            ]
        )

        # Mock output without pooler_output
        mock_outputs = MagicMock()
        mock_outputs.last_hidden_state = hidden_states
        self.mock_model.return_value = mock_outputs

        with patch("torch.no_grad"):
            result = adapter.encode("test text")

            # Calculate expected mean of the first 3 tokens (ignoring padding)
            # Mean of [1,2], [3,4], [5,6] = [3,4]
            expected = np.array([3.0, 4.0])
            np.testing.assert_array_equal(result, expected)

    def test_encode_max_pooling(self):
        """Test max pooling strategy."""
        # Create adapter with max pooling strategy
        adapter = HuggingFaceAdapter(self.mock_tokenizer, self.mock_model, "max")

        # Mock tokenizer output with attention mask
        attention_mask = torch.tensor([[1, 1, 1, 0]])  # 3 tokens + 1 padding
        mock_inputs = {
            "attention_mask": attention_mask,
            "input_ids": torch.ones((1, 4)),
        }
        self.mock_tokenizer.return_value = mock_inputs

        # Create hidden states with recognizable values
        hidden_states = torch.tensor(
            [
                [  # Batch dimension
                    [1.0, 2.0],  # Token 1
                    [3.0, 4.0],  # Token 2
                    [5.0, 6.0],  # Token 3
                    [7.0, 8.0],  # Padding (should be masked)
                ]
            ]
        )

        # Mock output without pooler_output
        mock_outputs = MagicMock()
        mock_outputs.last_hidden_state = hidden_states
        self.mock_model.return_value = mock_outputs

        # Call the actual encode method
        with patch("torch.no_grad"):
            result = adapter.encode("test text")

        # The expected result should be [5.0, 6.0] - the max values from the non-padded tokens
        expected = np.array([5.0, 6.0])
        np.testing.assert_array_equal(result, expected)

    def test_encode_invalid_pooling_strategy(self):
        """Test that an invalid pooling strategy raises an error."""
        # Create adapter with invalid pooling strategy
        adapter = HuggingFaceAdapter(self.mock_tokenizer, self.mock_model, "invalid")

        # Mock tokenizer output
        mock_inputs = {
            "attention_mask": torch.ones((1, 4)),
            "input_ids": torch.ones((1, 4)),
        }
        self.mock_tokenizer.return_value = mock_inputs

        # Mock output
        mock_outputs = MagicMock()
        mock_outputs.last_hidden_state = torch.rand((1, 4, 2))
        self.mock_model.return_value = mock_outputs

        # Expect ValueError when calling encode
        with patch("torch.no_grad"):
            with self.assertRaises(ValueError):
                adapter.encode("test text")


class TestOpenAIAdapter(unittest.TestCase):
    """Test cases for the OpenAIAdapter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.data = [MagicMock()]
        self.mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        self.mock_client.embeddings.create.return_value = self.mock_response

        self.adapter = OpenAIAdapter(self.mock_client)

    def test_encode_default_model(self):
        """Test encode method with default model."""
        result = self.adapter.encode("test text")

        # Check that the client's create method was called with the correct parameters
        self.mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small", input="test text"
        )

        # Check that the result is the expected numpy array
        np.testing.assert_array_equal(result, np.array([0.1, 0.2, 0.3]))

    def test_encode_custom_model(self):
        """Test encode method with custom model."""
        adapter = OpenAIAdapter(self.mock_client, model="text-embedding-3-large")
        result = adapter.encode("test text")

        # Check that the client's create method was called with the correct parameters
        self.mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-large", input="test text"
        )


class TestDummyEmbeddingModel(unittest.TestCase):
    """Test cases for the DummyEmbeddingModel class."""

    def test_encode_caching(self):
        """Test that encode method caches embeddings for the same text."""
        model = DummyEmbeddingModel(dimension=3, seed=42)

        # Encode the same text twice
        result1 = model.encode("test text")
        result2 = model.encode("test text")

        # Check that the results are the same
        np.testing.assert_array_equal(result1, result2)

        # Check that the dimension is correct
        self.assertEqual(result1.shape[0], 3)

        # Check that the vector is normalized
        self.assertAlmostEqual(np.linalg.norm(result1), 1.0, places=6)

    def test_encode_different_texts(self):
        """Test that encode method returns different embeddings for different texts."""
        model = DummyEmbeddingModel(dimension=3, seed=42)

        result1 = model.encode("text1")
        result2 = model.encode("text2")

        # Check that the results are different
        self.assertFalse(np.array_equal(result1, result2))

    def test_encode_reproducibility(self):
        """Test that encode method returns the same embeddings with the same seed."""
        model1 = DummyEmbeddingModel(dimension=3, seed=42)
        model2 = DummyEmbeddingModel(dimension=3, seed=42)

        result1 = model1.encode("test text")
        result2 = model2.encode("test text")

        # Check that the results are the same
        np.testing.assert_array_equal(result1, result2)

    def test_encode_different_seeds(self):
        """Test that encode method returns different embeddings with different seeds."""
        model1 = DummyEmbeddingModel(dimension=3, seed=42)
        model2 = DummyEmbeddingModel(dimension=3, seed=43)

        result1 = model1.encode("test text")
        result2 = model2.encode("test text")

        # Check that the results are different
        self.assertFalse(np.array_equal(result1, result2))


if __name__ == "__main__":
    unittest.main()
