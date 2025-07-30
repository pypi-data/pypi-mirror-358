"""
Advanced example of using the SemanticDictionary for practical applications.

This example demonstrates several real-world use cases for SemanticDictionary:
1. Building a FAQ system
2. Creating a command router
3. Implementing a configuration system with fuzzy key matching

Requirements:
- sentence-transformers package
"""

import json
from typing import Callable, Dict

from sentence_transformers import SentenceTransformer

from semantic_dictionary import SemanticDictionary, SentenceTransformerAdapter


def print_separator(title: str) -> None:
    """Print a separator with a title."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50 + "\n")


# Load a sentence-transformers model - using a small, fast model for the example
model = SentenceTransformer("all-MiniLM-L6-v2")
adapter = SentenceTransformerAdapter(model)


# Example 1: FAQ System
print_separator("FAQ System Example")

# Create a dictionary of FAQs with semantic matching
faqs = SemanticDictionary(adapter, similarity_threshold=0.75)

# Add some FAQ entries
faqs["How do I reset my password?"] = (
    "To reset your password, go to the login page and click on 'Forgot Password'."
)
faqs["How do I change my email address?"] = (
    "You can change your email in your account settings under 'Personal Information'."
)
faqs["What payment methods do you accept?"] = (
    "We accept credit cards, PayPal, and bank transfers."
)
faqs["How long does shipping take?"] = (
    "Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days."
)
faqs["Can I return a product?"] = (
    "Yes, you can return any product within 30 days of purchase for a full refund."
)

# Simulate user queries
user_queries = [
    "I forgot my password",
    "How can I update my email?",
    "What cards do you take for payment?",
    "How many days for delivery?",
    "I want to send back an item I bought",
    "Do you have a phone number?",  # This one shouldn't match any FAQ
]

print("FAQ System Demonstration:\n")
for query in user_queries:
    print(f"User Query: '{query}'")
    if query in faqs:
        print(f"Answer: {faqs[query]}")
    else:
        print("Sorry, I don't have information about that. Please contact support.")
    print()


# Example 2: Command Router
print_separator("Command Router Example")


# Define some command handlers
def show_help() -> str:
    """Show help information."""
    return "Available commands: help, status, users, settings"


def show_status() -> str:
    """Show system status."""
    return "System Status: All systems operational. CPU: 23%, Memory: 45%, Disk: 32%"


def list_users() -> str:
    """List all users."""
    return "Users: admin, john_doe, jane_smith"


def show_settings() -> str:
    """Show current settings."""
    return "Settings: Dark Mode: On, Notifications: Off, Auto-save: On"


# Create a command router with semantic matching
commands = SemanticDictionary(adapter, similarity_threshold=0.7)

# Register commands
commands["help"] = show_help
commands["show help"] = show_help
commands["status"] = show_status
commands["system status"] = show_status
commands["users"] = list_users
commands["list users"] = list_users
commands["settings"] = show_settings
commands["show settings"] = show_settings

# Simulate user inputs
user_inputs = [
    "I need help",
    "what's the current status",
    "show me all users",
    "display settings",
    "reboot system",  # This one shouldn't match any command
]

print("Command Router Demonstration:\n")
for user_input in user_inputs:
    print(f"User Input: '{user_input}'")
    if user_input in commands:
        # Call the handler function
        result = commands[user_input]()
        print(f"Response: {result}")
    else:
        print("Unknown command. Type 'help' for available commands.")
    print()


# Example 3: Configuration System with Fuzzy Key Matching
print_separator("Configuration System Example")

# Create a configuration system with semantic matching
config = SemanticDictionary(adapter, similarity_threshold=0.8)

# Define configuration sections
database_config = {
    "host": "localhost",
    "port": 5432,
    "username": "admin",
    "password": "secure_password",
    "database": "app_db",
}

logging_config = {
    "level": "INFO",
    "format": "json",
    "output": "logs/app.log",
    "rotate": True,
    "max_size": "10MB",
}

email_config = {
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "use_tls": True,
    "sender": "noreply@example.com",
    "templates_dir": "templates/email/",
}

# Add configurations to the dictionary
config["database settings"] = database_config
config["logging configuration"] = logging_config
config["email settings"] = email_config

# Simulate configuration lookups with different key phrasings
lookup_keys = [
    "database configuration",
    "logging settings",
    "email configuration",
    "cache settings",  # This one shouldn't match any config section
]

print("Configuration System Demonstration:\n")
for key in lookup_keys:
    print(f"Looking up: '{key}'")
    if key in config:
        # Pretty print the configuration
        print(f"Found configuration:")
        print(json.dumps(config[key], indent=2))
    else:
        print(f"No configuration found for '{key}'")
    print()


# Example 4: Combining Multiple Semantic Dictionaries
print_separator("Combined System Example")


# Create a master router that can handle different types of requests
def handle_request(request: str) -> str:
    """Handle a user request by routing to the appropriate system."""
    # Check if it's a FAQ question
    if request in faqs:
        return f"FAQ: {faqs[request]}"

    # Check if it's a command
    if request in commands:
        return f"Command: {commands[request]()}"

    # Default response
    return "I'm not sure how to help with that. Try asking about our FAQs, or use a command."


# Simulate a conversation
conversation = [
    "How do I reset my password?",
    "Show me the system status",
    "What payment methods are accepted?",
    "Show all users",
    "How do I cancel my subscription?",  # Not in FAQs
]

print("Combined System Demonstration:\n")
for request in conversation:
    print(f"User: {request}")
    response = handle_request(request)
    print(f"System: {response}")
    print()
