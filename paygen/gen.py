import multiprocessing
import json
import random

from faker import Faker
import numpy as np


# Performance related configuration
POOL_SIZE = multiprocessing.cpu_count()
USE_WEIGHTING = False
DEFAULT_MAX_SIZE = 1 * 1024 * 1024
DEFAULT_MIN_SIZE = 128
DEFAULT_ALPHA = 2.0
JSON_MIN_KEYS_PER_LEVEL = 2
JSON_MAX_KEYS_PER_LEVEL = 8
JSON_MAX_DEPTH = 3
JSON_NESTING_CHANCE = 0.3


def _gen_filesizes(samples, min_size, max_size):
    # Generate power law distribution with a bias towards smaller files
    sizes = 1 - np.random.power(DEFAULT_ALPHA, size=samples)
    # Scale sizes to our desired range
    sizes = min_size + (max_size - min_size) * sizes
    return [int(s) for s in sizes]


def _generate_text_payload(size: int) -> bytes:
    """Helper function to generate a single text payload."""
    fake = Faker(use_weighting=USE_WEIGHTING)
    # Generate text in larger chunks to reduce string concatenation
    chunks = []
    current_size = 0
    while current_size < size:
        # Ensure we generate at least 5 characters (Faker API requirement) and don't exceed our target size
        remaining = max(size - current_size, 5)
        chunk = fake.text(max_nb_chars=min(10000, remaining))
        chunks.append(chunk)
        current_size += len(chunk.encode('utf-8'))
    return ''.join(chunks).encode('utf-8')


def text_payloads(num_samples: int, min_size: int = DEFAULT_MIN_SIZE, max_size: int = DEFAULT_MAX_SIZE) -> list[bytes]:
    """Generate a list of text payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated text payloads as bytes
    """
    sizes = _gen_filesizes(num_samples, min_size, max_size)
    
    with multiprocessing.Pool(POOL_SIZE) as pool:
        return pool.map(_generate_text_payload, [int(s) for s in sizes])


def _generate_binary_payload(size: int) -> bytes:
    fake = Faker(use_weighting=USE_WEIGHTING)
    return fake.binary(length=size)


def binary_payloads(num_samples: int, min_size: int = DEFAULT_MIN_SIZE, max_size: int = DEFAULT_MAX_SIZE) -> list[bytes]:
    """Generate a list of binary payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated binary payloads
    """
    sizes = _gen_filesizes(num_samples, min_size, max_size)
    
    with multiprocessing.Pool(POOL_SIZE) as pool:
        return pool.map(_generate_binary_payload, sizes)


def _generate_json_payload(size: int) -> bytes:
    fake = Faker(use_weighting=USE_WEIGHTING)

    def generate_nested_value(depth=0):
        if depth > JSON_MAX_DEPTH or random.random() < JSON_NESTING_CHANCE:
            choices = [
                lambda: fake.text(max_nb_chars=100),
                lambda: random.randint(0, 1000000),
                lambda: random.choice([True, False]),
                lambda: None,
                lambda: [fake.text(max_nb_chars=50) for _ in range(random.randint(5, 20))],
            ]
            return fake.random_element(choices)()
        
        nested = {}
        for _ in range(random.randint(JSON_MIN_KEYS_PER_LEVEL, JSON_MAX_KEYS_PER_LEVEL)):
            nested[fake.word()] = generate_nested_value(depth + 1)
        return nested

    json_data = {}
    current_size = 0
    while current_size < size:
        for _ in range(random.randint(JSON_MIN_KEYS_PER_LEVEL, JSON_MAX_KEYS_PER_LEVEL)):
            key = fake.word()
            json_data[key] = generate_nested_value()
        current_size = len(json.dumps(json_data).encode('utf-8'))

    return json.dumps(json_data).encode('utf-8')


def json_payloads(num_samples: int, min_size: int = DEFAULT_MIN_SIZE, max_size: int = DEFAULT_MAX_SIZE) -> list[bytes]:
    """Generate a list of JSON payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated JSON payloads as bytes
    """
    sizes = _gen_filesizes(num_samples, min_size, max_size)
    
    with multiprocessing.Pool(POOL_SIZE) as pool:
        return pool.map(_generate_json_payload, sizes)