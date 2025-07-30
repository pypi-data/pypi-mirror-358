"""
Tests for the SemanticDictionary class.
"""

import math
import sys
import unittest
from unittest.mock import MagicMock

import numpy as np

from semantic_dictionary import (
    DummyEmbeddingModel,
    EmbeddingError,
    SemanticDictionary,
    ZeroVectorError,
)


class TestSemanticDictionary(unittest.TestCase):
    """Test cases for the SemanticDictionary class."""

    def setUp(self):
        """Set up test fixtures."""
        self.embedding_model = DummyEmbeddingModel(dimension=768, seed=42)
        self.sd = SemanticDictionary(self.embedding_model, similarity_threshold=0.7)

        # Add some items to the dictionary
        self.sd["apple"] = "A fruit"
        self.sd["banana"] = "A yellow fruit"
        self.sd["orange"] = "A citrus fruit"

    def test_key_access_methods(self):
        """Test key access methods: exact match, similar match, and no match."""
        # Test exact matches
        self.assertEqual(self.sd["apple"], "A fruit")
        self.assertEqual(self.sd["banana"], "A yellow fruit")
        self.assertEqual(self.sd["orange"], "A citrus fruit")

        # Test similar matches
        self.embedding_model.cache["apples"] = self.embedding_model.cache["apple"]
        self.embedding_model.cache["citrus"] = self.embedding_model.cache["orange"]

        self.assertEqual(self.sd["apples"], "A fruit")
        self.assertEqual(self.sd["citrus"], "A citrus fruit")

        # Test no match
        with self.assertRaises(KeyError):
            self.sd["car"]

        # Test get method
        self.assertEqual(self.sd.get("apple"), "A fruit")
        self.assertEqual(self.sd.get("citrus"), "A citrus fruit")
        self.assertEqual(self.sd.get("car", "Not found"), "Not found")
        self.assertIsNone(self.sd.get("car"))

        # Test contains
        self.assertIn("apple", self.sd)
        self.assertIn("citrus", self.sd)
        self.assertNotIn("car", self.sd)
        self.assertNotIn(123, self.sd)  # Non-string key

        # Test non-string keys
        with self.assertRaises(KeyError):
            value = self.sd[123]

        # Test setdefault
        value = self.sd.setdefault("apple", "Default value")
        self.assertEqual(value, "A fruit")

        self.embedding_model.cache["citrus"] = self.embedding_model.cache["orange"]
        value = self.sd.setdefault("citrus", "Default value")
        self.assertEqual(value, "A citrus fruit")

        value = self.sd.setdefault("grape", "A small fruit")
        self.assertEqual(value, "A small fruit")
        self.assertEqual(self.sd["grape"], "A small fruit")

    def test_modification_methods(self):
        """Test methods that modify the dictionary."""
        # Test deleting by exact key
        del self.sd["apple"]
        self.assertNotIn("apple", self.sd)

        # Test deleting by similar key
        self.embedding_model.cache["canine"] = self.embedding_model.cache["banana"]
        del self.sd["canine"]
        self.assertNotIn("banana", self.sd)

        # Test deleting a non-existent key
        with self.assertRaises(KeyError):
            del self.sd["car"]

        # Test non-string key for deletion
        with self.assertRaises(KeyError):
            del self.sd[123]

        # Test pop with exact key
        self.sd["apple"] = "A fruit"  # Add back for testing
        value = self.sd.pop("apple")
        self.assertEqual(value, "A fruit")
        self.assertNotIn("apple", self.sd)

        # Test pop with similar key
        self.sd["orange"] = "A citrus fruit"  # Add back for testing
        self.embedding_model.cache["citrus"] = self.embedding_model.cache["orange"]
        value = self.sd.pop("citrus")
        self.assertEqual(value, "A citrus fruit")
        self.assertNotIn("orange", self.sd)

        # Test pop with default value
        value = self.sd.pop("car", "Not found")
        self.assertEqual(value, "Not found")

        # Test pop with non-existent key and no default
        with self.assertRaises(KeyError):
            self.sd.pop("car")

        # Test popitem
        self.sd.clear()
        with self.assertRaises(KeyError):
            self.sd.popitem()

        self.sd["apple"] = "A fruit"
        key, value = self.sd.popitem()
        self.assertEqual(key, "apple")
        self.assertEqual(value, "A fruit")
        self.assertEqual(len(self.sd), 0)

        # Test clear
        self.sd["apple"] = "A fruit"
        self.sd["banana"] = "A yellow fruit"
        self.sd.clear()
        self.assertEqual(len(self.sd), 0)
        self.assertNotIn("apple", self.sd)
        self.assertNotIn("banana", self.sd)

    def test_dictionary_operations(self):
        """Test dictionary operations like update, copy, etc."""
        # Test update with dictionary
        self.sd.update({"grape": "A small fruit", "apple": "An overridden fruit"})
        self.assertEqual(self.sd["grape"], "A small fruit")
        self.assertEqual(self.sd["apple"], "An overridden fruit")

        # Test update with keyword arguments
        self.sd.update(kiwi="A fuzzy fruit", banana="A yellow curved fruit")
        self.assertEqual(self.sd["kiwi"], "A fuzzy fruit")
        self.assertEqual(self.sd["banana"], "A yellow curved fruit")

        # Test update with iterable of key-value pairs
        items = [("mango", "A tropical fruit"), ("grape", "A small round fruit")]
        self.sd.update(items)
        self.assertEqual(self.sd["mango"], "A tropical fruit")
        self.assertEqual(self.sd["grape"], "A small round fruit")

        # Test with too many arguments
        with self.assertRaises(TypeError):
            self.sd.update({}, {})

        # Test copy
        sd_copy = self.sd.copy()
        self.assertEqual(sd_copy, self.sd)

        # Modifying the copy should not affect the original
        sd_copy["apple"] = "A red fruit"
        self.assertNotEqual(sd_copy["apple"], self.sd["apple"])

        # Check that embeddings were copied
        self.assertEqual(sd_copy._embeddings, self.sd._embeddings)

        # Test sizeof
        size = sys.getsizeof(self.sd)
        self.assertGreater(size, 0)

    def test_comparison_and_operators(self):
        """Test comparison operators and dictionary operators."""
        # Create dictionaries for comparison
        sd1 = SemanticDictionary(self.embedding_model)
        sd1["a"] = 1
        sd1["b"] = 2

        sd2 = SemanticDictionary(self.embedding_model)
        sd2["a"] = 1
        sd2["b"] = 2
        sd2["c"] = 3

        # Test equality
        sd3 = SemanticDictionary(self.embedding_model)
        sd3["a"] = 1
        sd3["b"] = 2
        self.assertEqual(sd1, sd3)

        # Test with regular dictionary
        self.assertEqual(sd1, {"a": 1, "b": 2})

        # Test comparisons
        self.assertLess(sd1, sd2)
        self.assertLessEqual(sd1, sd2)
        self.assertLessEqual(sd1, sd1)
        self.assertGreater(sd2, sd1)
        self.assertGreaterEqual(sd2, sd1)
        self.assertGreaterEqual(sd2, sd2)

        # Test with equal dictionaries
        self.assertFalse(sd1 < sd3)
        self.assertFalse(sd1 > sd3)

        # Test with regular dict for comparison
        self.assertLess(sd1, {"a": 1, "b": 2, "c": 3})
        self.assertGreater(sd2, {"a": 1, "b": 2})

        # Test | operator
        other_dict = {"grape": "A small fruit", "apple": "An overridden fruit"}
        result = self.sd | other_dict

        self.assertIsInstance(result, SemanticDictionary)
        self.assertEqual(result["grape"], "A small fruit")
        self.assertEqual(result["apple"], "An overridden fruit")
        self.assertEqual(result["banana"], "A yellow fruit")
        self.assertEqual(result["orange"], "A citrus fruit")

        # Test |= operator
        sd_copy = self.sd.copy()
        sd_copy |= other_dict

        self.assertEqual(sd_copy["grape"], "A small fruit")
        self.assertEqual(sd_copy["apple"], "An overridden fruit")
        self.assertEqual(sd_copy["banana"], "A yellow fruit")
        self.assertEqual(sd_copy["orange"], "A citrus fruit")

        # Test __ror__ with dict
        result = other_dict | self.sd
        self.assertIsInstance(result, SemanticDictionary)
        self.assertEqual(result["grape"], "A small fruit")
        self.assertEqual(result["apple"], "A fruit")  # Original value preserved

        # Test operators with incompatible types
        self.assertEqual(self.sd.__eq__(123), NotImplemented)
        self.assertEqual(self.sd.__ne__(123), NotImplemented)
        self.assertEqual(self.sd.__lt__(123), NotImplemented)
        self.assertEqual(self.sd.__le__(123), NotImplemented)
        self.assertEqual(self.sd.__gt__(123), NotImplemented)
        self.assertEqual(self.sd.__ge__(123), NotImplemented)
        self.assertEqual(self.sd.__or__(123), NotImplemented)
        self.assertEqual(self.sd.__ior__(123), NotImplemented)
        self.assertEqual(self.sd.__ror__(123), NotImplemented)

        # Test specific comparison cases for line coverage
        # Test __gt__ with SemanticDictionary
        sd4 = SemanticDictionary(self.embedding_model)
        sd4["a"] = 1
        self.assertGreater(sd1, sd4)  # Covers line 362

        # Test __ge__ with SemanticDictionary
        self.assertGreaterEqual(sd1, sd4)  # Covers line 382

        # Test __eq__ with different lengths (line 342)
        self.assertNotEqual(sd1, sd4)

    def test_iteration_and_views(self):
        """Test iteration and dictionary views."""
        # Test keys, values, items
        keys = self.sd.keys()
        values = self.sd.values()
        items = self.sd.items()

        self.assertEqual(len(keys), 3)
        self.assertEqual(len(values), 3)
        self.assertEqual(len(items), 3)

        self.assertIn("apple", keys)
        self.assertIn("banana", keys)
        self.assertIn("orange", keys)

        self.assertIn("A fruit", values)
        self.assertIn("A yellow fruit", values)
        self.assertIn("A citrus fruit", values)

        self.assertIn(("apple", "A fruit"), items)
        self.assertIn(("banana", "A yellow fruit"), items)
        self.assertIn(("orange", "A citrus fruit"), items)

        # Test iteration
        keys_from_iter = []
        for key in self.sd:
            keys_from_iter.append(key)

        self.assertEqual(set(keys_from_iter), {"apple", "banana", "orange"})

        # Test reversed
        keys = list(reversed(self.sd))
        original_keys = list(self.sd.keys())
        self.assertEqual(keys, list(reversed(original_keys)))

        # Test len
        self.assertEqual(len(self.sd), 3)
        self.sd["grape"] = "A small fruit"
        self.assertEqual(len(self.sd), 4)

        # Test repr
        self.assertEqual(repr(self.sd), f"SemanticDictionary({repr(self.sd._data)})")

    def test_similarity_and_embedding_functions(self):
        """Test similarity calculation and embedding functions."""
        # Test _calculate_similarity caching
        self.sd._embeddings = {}
        similarity = self.sd._calculate_similarity("apple", "fruit")

        self.assertIn("apple", self.sd._embeddings)
        self.assertIn("fruit", self.sd._embeddings)

        # Test _find_similar_key exact match
        result = self.sd._find_similar_key("apple")
        self.assertEqual(result, "apple")

        # Test _find_similar_key no match
        result = self.sd._find_similar_key("computer")
        self.assertIsNone(result)

        # Test _find_similar_key with exact threshold
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([1.0, 0.0, 0.0])

        sd = SemanticDictionary(mock_model, similarity_threshold=1.0)
        sd["key1"] = "value1"

        similar_key = sd._find_similar_key("key2")
        self.assertEqual(similar_key, "key1")

        # Test _calculate_similarity with identical vectors
        mock_model = MagicMock()
        vec = np.array([0.1, 0.2, 0.3])
        mock_model.encode.return_value = vec

        sd = SemanticDictionary(mock_model)
        similarity = sd._calculate_similarity("key1", "key2")
        self.assertAlmostEqual(similarity, 1.0)

        # Test _calculate_similarity with zero vector
        mock_model = MagicMock()
        mock_model.encode.return_value = np.zeros(768)

        sd = SemanticDictionary(mock_model)

        with self.assertRaises(ZeroVectorError):
            sd._calculate_similarity("key1", "key2")

        # Test error handling in _get_embedding
        mock_model = MagicMock()
        mock_model.encode.return_value = np.zeros(768)
        sd = SemanticDictionary(mock_model)

        with self.assertRaises(ZeroVectorError):
            sd._get_embedding("test_key")

        mock_model.encode.side_effect = ValueError("Test error")
        sd = SemanticDictionary(mock_model)

        with self.assertRaises(EmbeddingError):
            sd._get_embedding("test_key")

    def test_miscellaneous(self):
        """Test miscellaneous functionality."""
        # Test default similarity threshold
        sd = SemanticDictionary(self.embedding_model)
        self.assertEqual(sd.similarity_threshold, 0.9)

        # Test setitem with non-string key
        try:
            self.sd[123] = "value"
            # Clean up after the test
            del self.sd._data[123]
            del self.sd._embeddings[123]
        except Exception as e:
            self.fail(f"__setitem__ with non-string key raised {e}")

        # Test fromkeys
        with self.assertRaises(TypeError):
            SemanticDictionary.fromkeys(["a", "b", "c"], "value")

    def test_special_cases(self):
        """Test special cases to improve coverage."""
        # Test line 342 - __eq__ with identical objects
        self.assertTrue(self.sd == self.sd)

        # Test line 426 - __ne__ with identical objects
        self.assertFalse(self.sd != self.sd)

        # Test line 548 - __ior__ with empty dict
        original_len = len(self.sd)
        self.sd |= {}
        self.assertEqual(len(self.sd), original_len)  # Should not change

        # Test line 404 - __le__ with identical objects
        sd1 = SemanticDictionary(self.embedding_model)
        sd1["a"] = 1
        sd1["b"] = 2

        sd2 = SemanticDictionary(self.embedding_model)
        sd2["a"] = 1
        sd2["b"] = 2

        # This specifically targets line 404 by testing equal dictionaries
        self.assertTrue(sd1 <= sd2)
        self.assertTrue(sd2 <= sd1)

        # Test line 449 - __or__ with empty dict and regular dict
        result = self.sd | {}
        self.assertEqual(len(result), len(self.sd))
        self.assertIsInstance(result, SemanticDictionary)

        # Additional test for __or__ with a regular dict
        regular_dict = {"new_key": "new_value"}
        result = self.sd | regular_dict
        self.assertIn("new_key", result)
        self.assertEqual(result["new_key"], "new_value")


if __name__ == "__main__":
    unittest.main()
