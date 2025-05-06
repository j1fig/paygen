import json
import numpy as np
from faker import Faker

# Performance related configuration
USE_WEIGHTING = False

def text_payloads(num_samples: int, min_size: int = 100, max_size: int = 1000000) -> list[bytes]:
    """Generate a list of text payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated text payloads as bytes
    """
    fake = Faker(use_weighting=USE_WEIGHTING)
    payloads = []
    
    # Generate power law distribution of sizes
    alpha = 2.0  # Typical power law exponent for text data
    sizes = np.random.power(alpha, size=num_samples)
    # Scale sizes to our desired range
    sizes = min_size + (max_size - min_size) * sizes
    
    for size in sizes:
        # Generate text in larger chunks to reduce string concatenation
        chunks = []
        current_size = 0
        while current_size < size:
            # Ensure we generate at least 5 characters (Faker API requirement) and don't exceed our target size
            remaining = max(size - current_size, 5)
            chunk = fake.text(max_nb_chars=min(10000, remaining))
            chunks.append(chunk)
            current_size += len(chunk.encode('utf-8'))
        payloads.append(''.join(chunks).encode('utf-8'))
        
    return payloads


def binary_payloads(num_samples: int, min_size: int = 100, max_size: int = 1000000) -> list[bytes]:
    """Generate a list of binary payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated binary payloads
    """
    fake = Faker(use_weighting=USE_WEIGHTING)
    payloads = []
    
    # Generate power law distribution of sizes
    alpha = 2.0  # Typical power law exponent for binary data
    sizes = np.random.power(alpha, size=num_samples)
    # Scale sizes to our desired range
    sizes = min_size + (max_size - min_size) * sizes
    
    for size in sizes:
        # Generate the entire binary payload at once
        payloads.append(fake.binary(length=int(size)))
        
    return payloads


def json_payloads(num_samples: int, min_size: int = 100, max_size: int = 1000000) -> list[bytes]:
    """Generate a list of JSON payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated JSON payloads as bytes
    """
    fake = Faker(use_weighting=USE_WEIGHTING)
    payloads = []
    
    # Generate power law distribution of sizes
    alpha = 2.0  # Typical power law exponent for JSON data
    sizes = np.random.power(alpha, size=num_samples)
    # Scale sizes to our desired range
    sizes = min_size + (max_size - min_size) * sizes

    def generate_nested_value(depth=0):
        if depth > 3 or fake.boolean(chance_of_getting_true=30):
            # Generate larger arrays and strings to reduce recursion
            choices = [
                lambda: fake.text(max_nb_chars=100),
                lambda: fake.random_number(),
                lambda: fake.boolean(),
                lambda: None,
                lambda: [fake.text(max_nb_chars=50) for _ in range(fake.random_int(min=5, max=20))],
            ]
            return fake.random_element(choices)()
        
        nested = {}
        # Generate more keys at once to reduce recursion
        for _ in range(fake.random_int(min=5, max=15)):
            nested[fake.word()] = generate_nested_value(depth + 1)
        return nested

    for size in sizes:
        json_data = {}
        current_size = 0
        while current_size < size:
            # Generate more keys at once to reduce iterations
            for _ in range(fake.random_int(min=5, max=15)):
                key = fake.word()
                json_data[key] = generate_nested_value()
            current_size = len(json.dumps(json_data).encode('utf-8'))
        payloads.append(json.dumps(json_data).encode('utf-8'))
        
    return payloads