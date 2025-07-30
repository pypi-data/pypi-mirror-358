# Semantic Dictionary

A dictionary-like class that uses semantic similarity for key matching instead of exact matches.

## Features

- **Drop-in replacement for dict**: Implements the complete standard dictionary interface
- **Semantic matching**: Find keys based on semantic similarity, not just exact matches
- **Flexible embedding**: Works with various embedding models (sentence-transformers, Hugging Face, OpenAI)
- **Type annotations**: Fully typed with generics support

## Installation

You can install the package from PyPI:

```bash
pip install semantic-dictionary
```

For additional functionality, you can install optional dependencies:

```bash
# For sentence-transformers support
pip install semantic-dictionary[sentence-transformers]

# For Hugging Face support
pip install semantic-dictionary[huggingface]

# For OpenAI support
pip install semantic-dictionary[openai]

# For all optional dependencies
pip install semantic-dictionary[all]
```

## Quick Start Guide

Get up and running with SemanticDictionary in just a few steps:

1. **Install the package with your preferred embedding model**:
   ```bash
   pip install semantic-dictionary[sentence-transformers]
   ```

2. **Create a simple dictionary**:
   ```python
   from semantic_dictionary import SemanticDictionary, SentenceTransformerAdapter
   from sentence_transformers import SentenceTransformer
   
   # Initialize the embedding model and adapter
   model = SentenceTransformer('all-MiniLM-L6-v2')
   adapter = SentenceTransformerAdapter(model)
   
   # Create the semantic dictionary with a similarity threshold
   sd = SemanticDictionary(adapter, similarity_threshold=0.75)
   
   # Add some items
   sd["customer support"] = "Help desk contact information"
   sd["product pricing"] = "Current product price list"
   sd["shipping policy"] = "Information about shipping options"
   ```

3. **Use semantic lookups**:
   ```python
   # These will work even though the keys don't exactly match
   print(sd["customer help"])  # Returns "Help desk contact information"
   print(sd["price list"])     # Returns "Current product price list"
   print(sd["delivery info"])  # Returns "Information about shipping options"
   
   # Check if semantically similar keys exist
   if "refund policy" in sd:
       print("Refund information found!")
   else:
       print("No refund information available")
   ```

4. **Adjust the similarity threshold** as needed for your use case:
   ```python
   # More strict matching (closer to 1.0)
   strict_sd = SemanticDictionary(adapter, similarity_threshold=0.9)
   
   # More lenient matching (closer to 0.0)
   lenient_sd = SemanticDictionary(adapter, similarity_threshold=0.6)
   ```

## Documentation

- [Examples](examples/) - Check out various examples, including:
  - [Basic Example](examples/basic_example.py) - Simple demonstration of core functionality
  - [Sentence Transformers Example](examples/sentence_transformers_example.py) - Using with sentence-transformers
  - [Advanced Example](examples/advanced_example.py) - Real-world use cases like FAQ systems, command routing, and more

## Error Handling

SemanticDictionary provides exceptions representing common issues:

### Key Exceptions

- **KeyError**: Raised when no semantically similar key is found
- **ZeroVectorError**: Raised when a zero vector is encountered during similarity calculation
- **EmbeddingError**: Raised when there's a problem with embedding generation

### Handling Errors

```python
from semantic_dictionary import SemanticDictionary, ZeroVectorError, EmbeddingError

# Create your semantic dictionary
sd = SemanticDictionary(embedding_model)

try:
    value = sd["some_key"]
except KeyError:
    print("No similar key found")
except ZeroVectorError as e:
    print(f"Zero vector issue: {e}")
except EmbeddingError as e:
    print(f"Embedding error: {e}")
```

## Usage

### Basic Usage

```python
from semantic_dictionary import SemanticDictionary, DummyEmbeddingModel

# Create a dummy embedding model for demonstration
embedding_model = DummyEmbeddingModel(dimension=768, seed=42)

# Create a semantic dictionary with a similarity threshold of 0.7
sd = SemanticDictionary(embedding_model, similarity_threshold=0.7)

# Add items to the dictionary
sd["apple"] = "A fruit"
sd["banana"] = "A yellow fruit"
sd["orange"] = "A citrus fruit"

# Retrieve items using semantically similar keys
print(sd["apples"])  # Output: "A fruit"
print(sd["citrus"])  # Output: "A citrus fruit"
print(sd["yellow"])  # Output: KeyError (if similarity is below threshold)

# Check if a key exists
print("apples" in sd)  # Output: True (if similarity is above threshold)
print("car" in sd)     # Output: False

# Get a value with a default
print(sd.get("apples", "Not found"))  # Output: "A fruit"
print(sd.get("car", "Not found"))     # Output: "Not found"
```

## Semantic vs. Standard Dictionary Behavior

It's important to understand when semantic similarity is used versus standard dictionary behavior:

### Operations Using Semantic Similarity
- **Key lookups**: `sd[key]`, `sd.get(key)`, `key in sd`
- **Key deletion**: `del sd[key]`, `sd.pop(key)`
- **Key checking**: `key in sd`
- **Key finding**: `sd.setdefault(key, default)`

### Operations Using Standard Dictionary Behavior
- **Dictionary merging**: `sd | other_dict`, `sd |= other_dict`, `sd.update(other_dict)`
- **Dictionary comparison**: `sd == other_dict`, `sd != other_dict`, `sd < other_dict`, etc.
- **Dictionary iteration**: `sd.keys()`, `sd.values()`, `sd.items()`, `iter(sd)`

This distinction is crucial to understand when working with SemanticDictionary, as it affects how keys are matched and processed.

### Using with Sentence Transformers

```python
from semantic_dictionary import SemanticDictionary, SentenceTransformerAdapter
from sentence_transformers import SentenceTransformer

# Load a sentence-transformers model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create an adapter for the model
adapter = SentenceTransformerAdapter(model)

# Create a semantic dictionary with the adapter
sd = SemanticDictionary(adapter, similarity_threshold=0.7)

# Use the dictionary as before
sd["apple"] = "A fruit"
sd["banana"] = "A yellow fruit"
sd["orange"] = "A citrus fruit"

print(sd["fruit"])  # Will match the most similar key
```

### Using with Hugging Face Transformers

```python
from semantic_dictionary import SemanticDictionary, HuggingFaceAdapter
from transformers import AutoTokenizer, AutoModel

# Load a Hugging Face model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModel.from_pretrained('bert-base-uncased')

# Create an adapter for the model
adapter = HuggingFaceAdapter(tokenizer, model, pooling_strategy='mean')

# Create a semantic dictionary with the adapter
sd = SemanticDictionary(adapter, similarity_threshold=0.7)

# Use the dictionary as before
sd["apple"] = "A fruit"
sd["banana"] = "A yellow fruit"
sd["orange"] = "A citrus fruit"

print(sd["fruit"])  # Will match the most similar key
```

### Using with OpenAI

```python
from semantic_dictionary import SemanticDictionary, OpenAIAdapter
from openai import OpenAI

# Create an OpenAI client
client = OpenAI(api_key="your-api-key")

# Create an adapter for OpenAI
adapter = OpenAIAdapter(client, model="text-embedding-3-small")

# Create a semantic dictionary with the adapter
sd = SemanticDictionary(adapter, similarity_threshold=0.7)

# Use the dictionary as before
sd["apple"] = "A fruit"
sd["banana"] = "A yellow fruit"
sd["orange"] = "A citrus fruit"

print(sd["fruit"])  # Will match the most similar key
```

## Getting Help

If you encounter issues, please open an issue on the GitHub repository with a minimal reproducible example.

## Development

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/eu90h/semantic-dictionary.git
   cd semantic-dictionary
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[all]"
   pip install -r requirements-dev.txt
   ```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black semantic_dictionary tests examples
isort semantic_dictionary tests examples
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 