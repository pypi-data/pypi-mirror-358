"""
SemanticDictionary module.

This module provides a dictionary-like class that uses semantic similarity
for key matching instead of exact matches.

Semantic similarity is used for:
- Key lookups (__getitem__, get, __contains__)
- Key deletion (__delitem__, pop)
- Key checking (in operator)
- Key finding (setdefault)

Standard dictionary behavior is used for:
- Dictionary merging (|, |=, update)
- Dictionary comparison (==, !=, <, <=, >, >=)
- Dictionary iteration (keys, values, items, __iter__)
"""

from collections.abc import MutableMapping
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
    Union,
)

import numpy as np


class ZeroVectorError(ValueError):
    """Error raised when a zero vector is encountered during similarity calculation."""

    pass


class EmbeddingError(RuntimeError):
    """Error raised when there's a problem with embedding generation."""

    pass


T = TypeVar("T")  # Type variable for dictionary values


class EmbeddingModelProtocol(Protocol):
    """Protocol defining the required interface for embedding models."""

    def encode(self, text: str) -> np.ndarray:
        """
        Encode a text string into an embedding vector.

        Args:
            text: The text to encode

        Returns:
            A numpy array representing the embedding vector
        """
        ...


class SemanticDictionary(MutableMapping, Generic[T]):
    """
    A dictionary-like class that uses semantic similarity for key matching.

    The SemanticDictionary behaves like a standard Python dictionary, but when
    looking up keys, it will return values for keys that are semantically similar
    to the lookup key if an exact match is not found.

    Semantic similarity is used for:
    - Key lookups (dict[key], get(), in operator)
    - Key deletion (del dict[key], pop())
    - Key checking (key in dict)
    - Key finding (setdefault())

    Standard dictionary behavior is used for:
    - Dictionary merging (|, |=, update())
    - Dictionary comparison (==, !=, <, <=, >, >=)
    - Dictionary iteration (keys(), values(), items(), iter())

    Attributes:
        similarity_threshold: The minimum similarity score required for a match
        embedding_model: The model used to generate embeddings for keys
    """

    def __init__(
        self,
        embedding_model: EmbeddingModelProtocol,
        similarity_threshold: float = 0.9,
        initial_data: Optional[Dict[str, T]] = None,
    ):
        """
        Initialize a new SemanticDictionary.

        Args:
            embedding_model: A model that provides an encode method to convert strings to embeddings.
                Must implement the encode(text: str) -> np.ndarray method.
            similarity_threshold: The minimum similarity score required for a match (0.0 to 1.0)
            initial_data: Initial data to populate the dictionary with

        Raises:
            ValueError: If similarity_threshold is not between 0.0 and 1.0
        """
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError(
                f"similarity_threshold must be between 0.0 and 1.0, got {similarity_threshold}"
            )

        self._data: Dict[str, T] = {}
        self._embeddings: Dict[str, np.ndarray] = {}
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold

        if initial_data:
            self.update(initial_data)

    def _get_embedding(self, key: str) -> np.ndarray:
        """
        Get or compute the embedding for a key.

        Args:
            key: The key to get the embedding for

        Returns:
            The embedding vector for the key

        Raises:
            EmbeddingError: If there's an error generating the embedding
            ZeroVectorError: If the generated embedding is a zero vector
        """
        if key not in self._embeddings:
            try:
                embedding = self.embedding_model.encode(key)

                # Check for zero vector
                if np.all(embedding == 0) or np.linalg.norm(embedding) < 1e-10:
                    raise ZeroVectorError(
                        f"Embedding model returned a zero vector for key '{key}'. "
                        "This can happen with very short or unusual inputs."
                    )

                self._embeddings[key] = embedding
            except Exception as e:
                if isinstance(e, ZeroVectorError):
                    raise
                raise EmbeddingError(
                    f"Error generating embedding for key '{key}': {str(e)}"
                ) from e

        return self._embeddings[key]

    def _calculate_similarity(self, key1: str, key2: str) -> float:
        """
        Calculate the semantic similarity between two keys.

        Args:
            key1: The first key
            key2: The second key

        Returns:
            A similarity score between 0.0 and 1.0, where 1.0 is identical

        Raises:
            ZeroVectorError: If any of the embedding vectors is a zero vector
            EmbeddingError: If there's an error generating the embeddings
        """
        # Get embeddings
        vec1 = self._get_embedding(key1)
        vec2 = self._get_embedding(key2)

        # Calculate norms
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        # Check for zero vectors
        if norm1 < 1e-10 or norm2 < 1e-10:
            raise ZeroVectorError(
                f"Cannot calculate similarity between '{key1}' and '{key2}': "
                "One or both embeddings are zero vectors."
            )

        # Normalize vectors
        vec1_norm = vec1 / norm1
        vec2_norm = vec2 / norm2

        # Calculate cosine similarity
        similarity = np.dot(vec1_norm, vec2_norm)

        return float(similarity)

    def _find_similar_key(self, key: str) -> Optional[str]:
        """
        Find a key in the dictionary that is semantically similar to the given key.

        Args:
            key: The key to find a similar match for

        Returns:
            The most similar key if one exists with similarity above the threshold,
            or None if no similar key is found

        Raises:
            EmbeddingError: If there's an error generating the embeddings
        """
        # Return exact match if it exists
        if key in self._data:
            return key

        # Find the most similar key
        best_match = None
        best_similarity = 0.0

        try:
            for existing_key in self._data.keys():
                try:
                    similarity = self._calculate_similarity(key, existing_key)
                    if (
                        similarity > best_similarity
                        and similarity >= self.similarity_threshold
                    ):
                        best_similarity = similarity
                        best_match = existing_key
                except ZeroVectorError:
                    # Skip this key if we get a zero vector error
                    continue
        except EmbeddingError as e:
            # Re-raise embedding errors with more context
            raise EmbeddingError(
                f"Error finding similar key for '{key}': {str(e)}"
            ) from e

        return best_match

    def __getitem__(self, key: str) -> T:
        """
        Get an item from the dictionary using semantic matching.

        This method uses semantic similarity to find keys. If an exact match is not found,
        it will return the value for the most semantically similar key that exceeds the
        similarity threshold.

        Args:
            key: The key to look up

        Returns:
            The value associated with the most similar key

        Raises:
            KeyError: If no similar key is found
        """
        similar_key = self._find_similar_key(key)
        if similar_key is not None:
            return self._data[similar_key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: T) -> None:
        """
        Set an item in the dictionary.

        Args:
            key: The key to set
            value: The value to associate with the key
        """
        if key not in self._embeddings:
            self._embeddings[key] = self.embedding_model.encode(key)

        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        """
        Delete an item from the dictionary.

        This method uses semantic similarity to find keys. If an exact match is not found,
        it will delete the most semantically similar key that exceeds the similarity threshold.

        Args:
            key: The key to delete

        Raises:
            KeyError: If no similar key is found
        """
        similar_key = self._find_similar_key(key)
        if similar_key is not None:
            del self._data[similar_key]
        else:
            raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator over the keys in the dictionary.

        Returns:
            An iterator over the keys
        """
        return iter(self._data)

    def __len__(self) -> int:
        """
        Return the number of items in the dictionary.

        Returns:
            The number of items
        """
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        """
        Check if a key exists in the dictionary using semantic matching.

        This method uses semantic similarity to find keys. It will return True if
        either an exact match exists or if a semantically similar key (exceeding the
        similarity threshold) is found.

        Args:
            key: The key to check

        Returns:
            True if a similar key exists, False otherwise
        """
        if not isinstance(key, str):
            return False

        return self._find_similar_key(key) is not None

    def __eq__(self, other: object) -> bool:
        """
        Compare the dictionary with another object for equality.

        Args:
            other: The object to compare with

        Returns:
            True if the objects are equal, False otherwise
        """
        if not isinstance(other, dict) and not isinstance(other, SemanticDictionary):
            return NotImplemented

        if len(self) != len(other):
            return False

        if isinstance(other, dict):
            return self._data == other

        return self._data == other._data

    def __ne__(self, other: object) -> bool:
        """
        Compare the dictionary with another object for inequality.

        Args:
            other: The object to compare with

        Returns:
            True if the objects are not equal, False otherwise
        """
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __lt__(self, other: object) -> bool:
        """
        Compare if the dictionary is less than another object.

        Args:
            other: The object to compare with

        Returns:
            True if the dictionary is less than the other object, False otherwise
        """
        if not isinstance(other, dict) and not isinstance(other, SemanticDictionary):
            return NotImplemented

        self_items = sorted(self._data.items())

        if isinstance(other, SemanticDictionary):
            other_items = sorted(other._data.items())
        else:
            other_items = sorted(other.items())

        return self_items < other_items

    def __le__(self, other: object) -> bool:
        """
        Compare if the dictionary is less than or equal to another object.

        Args:
            other: The object to compare with

        Returns:
            True if the dictionary is less than or equal to the other object, False otherwise
        """
        if not isinstance(other, dict) and not isinstance(other, SemanticDictionary):
            return NotImplemented

        self_items = sorted(self._data.items())

        if isinstance(other, SemanticDictionary):
            other_items = sorted(other._data.items())
        else:
            other_items = sorted(other.items())

        return self_items <= other_items

    def __gt__(self, other: object) -> bool:
        """
        Compare if the dictionary is greater than another object.

        Args:
            other: The object to compare with

        Returns:
            True if the dictionary is greater than the other object, False otherwise
        """
        if not isinstance(other, dict) and not isinstance(other, SemanticDictionary):
            return NotImplemented

        self_items = sorted(self._data.items())

        if isinstance(other, SemanticDictionary):
            other_items = sorted(other._data.items())
        else:
            other_items = sorted(other.items())

        return self_items > other_items

    def __ge__(self, other: object) -> bool:
        """
        Compare if the dictionary is greater than or equal to another object.

        Args:
            other: The object to compare with

        Returns:
            True if the dictionary is greater than or equal to the other object, False otherwise
        """
        if not isinstance(other, dict) and not isinstance(other, SemanticDictionary):
            return NotImplemented

        # Convert dictionaries to sorted tuples of items for comparison
        self_items = sorted(self._data.items())

        if isinstance(other, SemanticDictionary):
            other_items = sorted(other._data.items())
        else:
            other_items = sorted(other.items())

        return self_items >= other_items

    def __or__(self, other: object) -> "SemanticDictionary[T]":
        """
        Return a new dictionary with the merged contents of the dictionary and another object.

        Note: This operation uses standard dictionary merging behavior, not semantic similarity.
        Keys are merged exactly as they appear, without considering semantic similarity between keys.

        Args:
            other: The object to merge with

        Returns:
            A new SemanticDictionary with the merged contents

        Raises:
            TypeError: If the other object is not a mapping
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        result = self.copy()
        result.update(other)
        return result

    def __ior__(self, other: object) -> "SemanticDictionary[T]":
        """
        Update the dictionary with the contents of another object.

        Note: This operation uses standard dictionary merging behavior, not semantic similarity.
        Keys are merged exactly as they appear, without considering semantic similarity between keys.

        Args:
            other: The object to update with

        Returns:
            The updated dictionary

        Raises:
            TypeError: If the other object is not a mapping
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        self.update(other)
        return self

    def __ror__(self, other: object) -> "SemanticDictionary[T]":
        """
        Return a new dictionary with the merged contents of another object and the dictionary.

        Note: This operation uses standard dictionary merging behavior, not semantic similarity.
        Keys are merged exactly as they appear, without considering semantic similarity between keys.

        Args:
            other: The object to merge with

        Returns:
            A new SemanticDictionary with the merged contents

        Raises:
            TypeError: If the other object is not a mapping
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        result = self.copy()
        for key in other:
            if key not in result:
                result[key] = other[key]
        return result

    def __repr__(self) -> str:
        """
        Return a string representation of the dictionary.

        Returns:
            A string representation of the dictionary
        """
        return f"{self.__class__.__name__}({repr(self._data)})"

    def __reversed__(self) -> Iterator[str]:
        """
        Return a reverse iterator over the dictionary keys.

        Returns:
            A reverse iterator over the keys
        """
        return reversed(self._data.keys())

    def __sizeof__(self) -> int:
        """
        Return the size of the dictionary in memory, in bytes.

        Returns:
            The size of the dictionary in memory, in bytes
        """
        return self._data.__sizeof__() + sum(
            e.__sizeof__() for e in self._embeddings.values()
        )

    @classmethod
    def fromkeys(cls, iterable: Iterable, value: Any = None) -> "SemanticDictionary":
        """
        Create a new dictionary with keys from iterable and values set to value.

        Args:
            iterable: The iterable containing the keys
            value: The value to set for all keys

        Returns:
            A new SemanticDictionary with the specified keys and values

        Raises:
            TypeError: If the embedding_model is not provided
        """
        raise TypeError(
            f"{cls.__name__}.fromkeys() requires an embedding_model. "
            f"Use {cls.__name__}(embedding_model, initial_data=dict.fromkeys(iterable, value)) instead."
        )

    def get(self, key: str, default: Any = None) -> Union[T, Any]:
        """
        Get an item from the dictionary using semantic matching.

        This method uses semantic similarity to find keys. If an exact match is not found,
        it will return the value for the most semantically similar key that exceeds the
        similarity threshold.

        Args:
            key: The key to look up
            default: The value to return if no similar key is found

        Returns:
            The value associated with the most similar key, or the default value
        """
        try:
            return self[key]
        except KeyError:
            return default

    def clear(self) -> None:
        """Clear all items from the dictionary."""
        self._data.clear()

    def copy(self) -> "SemanticDictionary[T]":
        """
        Return a shallow copy of the dictionary.

        Returns:
            A new SemanticDictionary with the same contents
        """
        result = SemanticDictionary(self.embedding_model, self.similarity_threshold)
        result._data = self._data.copy()
        result._embeddings = self._embeddings.copy()
        return result

    def pop(self, key: str, default: Any = None) -> Union[T, Any]:
        """
        Remove and return an item from the dictionary.

        This method uses semantic similarity to find keys. If an exact match is not found,
        it will remove and return the value for the most semantically similar key that exceeds
        the similarity threshold.

        Args:
            key: The key to remove
            default: The value to return if no similar key is found

        Returns:
            The value associated with the removed key

        Raises:
            KeyError: If no similar key is found and no default is provided
        """
        similar_key = self._find_similar_key(key)
        if similar_key is not None:
            value = self._data[similar_key]
            del self._data[similar_key]
            return value
        if default is not None:
            return default
        raise KeyError(key)

    def popitem(self) -> Tuple[str, T]:
        """
        Remove and return an arbitrary item from the dictionary.

        Returns:
            A (key, value) tuple

        Raises:
            KeyError: If the dictionary is empty
        """
        if not self._data:
            raise KeyError("popitem(): dictionary is empty")

        key, value = next(iter(self._data.items()))
        del self._data[key]
        return key, value

    def setdefault(self, key: str, default: T = None) -> T:
        """
        Insert key with a value of default if key is not in the dictionary.

        This method uses semantic similarity to find keys. If neither an exact match
        nor a semantically similar key (exceeding the similarity threshold) is found,
        it will insert the key with the default value.

        Args:
            key: The key to look up
            default: The value to set if the key is not found

        Returns:
            The value for key if key is in the dictionary, else default
        """
        similar_key = self._find_similar_key(key)
        if similar_key is not None:
            return self._data[similar_key]
        self[key] = default
        return default

    def keys(self) -> Iterable[str]:
        """
        Return a set-like object providing a view on the dictionary's keys.

        Returns:
            A view of the dictionary's keys
        """
        return self._data.keys()

    def values(self) -> List[T]:
        """
        Return a list-like object providing a view on the dictionary's values.

        Returns:
            A view of the dictionary's values
        """
        return list(self._data.values())

    def items(self) -> Set[Tuple[str, T]]:
        """
        Return a set-like object providing a view on the dictionary's items.

        Returns:
            A view of the dictionary's items
        """
        return set(self._data.items())

    def update(self, *args, **kwargs) -> None:
        """
        Update the dictionary with the key/value pairs from other.

        Note: This operation uses standard dictionary update behavior, not semantic similarity.
        Keys are added exactly as they appear, without considering semantic similarity between keys.

        Args:
            *args: Either a dictionary or an iterable of key/value pairs
            **kwargs: Keyword arguments to add to the dictionary
        """
        if args:
            if len(args) > 1:
                raise TypeError(
                    "update expected at most 1 argument, got %d" % len(args)
                )

            other = args[0]
            if isinstance(other, dict):
                for key in other:
                    self[key] = other[key]
            else:
                for key, value in other:
                    self[key] = value

        for key, value in kwargs.items():
            self[key] = value
