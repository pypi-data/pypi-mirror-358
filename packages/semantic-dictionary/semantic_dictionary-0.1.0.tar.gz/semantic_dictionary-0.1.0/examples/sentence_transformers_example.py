"""
Example of using the SemanticDictionary with sentence-transformers.

This example demonstrates how to use SemanticDictionary with the sentence-transformers
library for real semantic similarity matching.

Requirements:
- sentence-transformers package
"""

from sentence_transformers import SentenceTransformer

from semantic_dictionary import SemanticDictionary, SentenceTransformerAdapter

# Load a sentence-transformers model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create an adapter for the model
adapter = SentenceTransformerAdapter(model)

# Create a semantic dictionary with the adapter
sd = SemanticDictionary(adapter, similarity_threshold=0.7)

# Add items to the dictionary
sd["apple"] = "A round fruit with red, green, or yellow skin"
sd["banana"] = "A long curved fruit with a yellow skin"
sd["orange"] = "A round citrus fruit with orange skin"
sd["grape"] = "A small juicy fruit growing in clusters"
sd["strawberry"] = "A red heart-shaped fruit with seeds on the outside"
sd["blueberry"] = "A small blue-purple berry"

# Try to retrieve items using semantically similar keys
print("Retrieving with semantically similar keys:")
try:
    print(f"sd['red fruit'] = {sd['red fruit']}")  # Should match strawberry or apple
except KeyError:
    print("'red fruit' not found")

try:
    print(
        f"sd['yellow curved fruit'] = {sd['yellow curved fruit']}"
    )  # Should match banana
except KeyError:
    print("'yellow curved fruit' not found")

try:
    print(f"sd['citrus'] = {sd['citrus']}")  # Should match orange
except KeyError:
    print("'citrus' not found")

try:
    print(f"sd['small berry'] = {sd['small berry']}")  # Should match blueberry or grape
except KeyError:
    print("'small berry' not found")

# Check if semantically similar keys exist
print("\nChecking if semantically similar keys exist:")
print(f"'red fruit' in sd = {'red fruit' in sd}")
print(f"'yellow curved fruit' in sd = {'yellow curved fruit' in sd}")
print(f"'citrus' in sd = {'citrus' in sd}")
print(f"'small berry' in sd = {'small berry' in sd}")
print(f"'vegetable' in sd = {'vegetable' in sd}")  # Should be False

# Get values with defaults for semantically similar keys
print("\nGetting values with defaults:")
print(f"sd.get('red fruit', 'Not found') = {sd.get('red fruit', 'Not found')}")
print(f"sd.get('vegetable', 'Not found') = {sd.get('vegetable', 'Not found')}")

# Update the dictionary with new items
print("\nUpdating the dictionary:")
sd.update(
    {
        "watermelon": "A large green fruit with red flesh and black seeds",
        "pineapple": "A tropical fruit with a tough spiky skin and sweet yellow flesh",
    }
)
print(f"After update, sd has {len(sd)} items")

# Try to retrieve the new items with semantically similar keys
try:
    print(
        f"sd['tropical sweet fruit'] = {sd['tropical sweet fruit']}"
    )  # Should match pineapple
except KeyError:
    print("'tropical sweet fruit' not found")

try:
    print(
        f"sd['large green fruit'] = {sd['large green fruit']}"
    )  # Should match watermelon
except KeyError:
    print("'large green fruit' not found")
