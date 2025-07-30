"""
Basic example of using the SemanticDictionary with the DummyEmbeddingModel.
"""

from semantic_dictionary import DummyEmbeddingModel, SemanticDictionary

# Create a dummy embedding model for demonstration
embedding_model = DummyEmbeddingModel(dimension=768, seed=42)

# Create a semantic dictionary with a similarity threshold of 0.7
sd = SemanticDictionary(embedding_model, similarity_threshold=0.7)

# Add items to the dictionary
sd["apple"] = "A fruit"
sd["banana"] = "A yellow fruit"
sd["orange"] = "A citrus fruit"

# Make some keys similar for demonstration purposes
embedding_model.cache["apples"] = embedding_model.cache["apple"]
embedding_model.cache["citrus"] = embedding_model.cache["orange"]
embedding_model.cache["yellow"] = embedding_model.cache["banana"]

# Retrieve items using semantically similar keys
print("Retrieving with similar keys:")
print(f"sd['apples'] = {sd['apples']}")
print(f"sd['citrus'] = {sd['citrus']}")
print(f"sd['yellow'] = {sd['yellow']}")

# Check if a key exists
print("\nChecking if keys exist:")
print(f"'apples' in sd = {'apples' in sd}")
print(f"'citrus' in sd = {'citrus' in sd}")
print(f"'car' in sd = {'car' in sd}")

# Get a value with a default
print("\nGetting values with defaults:")
print(f"sd.get('apples', 'Not found') = {sd.get('apples', 'Not found')}")
print(f"sd.get('car', 'Not found') = {sd.get('car', 'Not found')}")

# Update the dictionary
print("\nUpdating the dictionary:")
sd.update({"grape": "A small fruit", "watermelon": "A large fruit"})
print(f"After update, sd has {len(sd)} items")
print(f"sd['grape'] = {sd['grape']}")
print(f"sd['watermelon'] = {sd['watermelon']}")

# Delete an item
print("\nDeleting an item:")
del sd["apple"]
print(f"After deletion, 'apple' in sd = {'apple' in sd}")
print(f"After deletion, 'apples' in sd = {'apples' in sd}")

# Pop an item
print("\nPopping an item:")
value = sd.pop("citrus")
print(f"Popped value = {value}")
print(f"After pop, 'orange' in sd = {'orange' in sd}")
print(f"After pop, 'citrus' in sd = {'citrus' in sd}")

# Clear the dictionary
print("\nClearing the dictionary:")
sd.clear()
print(f"After clear, sd has {len(sd)} items")
