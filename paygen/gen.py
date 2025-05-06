import multiprocessing
import json
import random
import uuid
from tqdm import tqdm

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
CHUNK_SIZE = 16384  # 16KB chunks for streaming


def text_payloads(num_samples: int, min_size: int = DEFAULT_MIN_SIZE, max_size: int = DEFAULT_MAX_SIZE) -> list[bytes]:
    """Generate a list of text payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated text payloads as bytes
    """
    _queue_gen(_generate_text_payload, num_samples, min_size, max_size)


def binary_payloads(num_samples: int, min_size: int = DEFAULT_MIN_SIZE, max_size: int = DEFAULT_MAX_SIZE) -> list[bytes]:
    """Generate a list of binary payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated binary payloads
    """
    _queue_gen(_generate_binary_payload, num_samples, min_size, max_size)


def json_payloads(num_samples: int, min_size: int = DEFAULT_MIN_SIZE, max_size: int = DEFAULT_MAX_SIZE) -> list[bytes]:
    """Generate a list of JSON payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated JSON payloads as bytes
    """
    _queue_gen(_generate_json_payload, num_samples, min_size, max_size)


def _queue_gen(gen_fn, num_samples, max_size, min_size):
    sizes = _gen_filesizes(num_samples, min_size, max_size)
    
    with multiprocessing.Pool(POOL_SIZE) as pool:
        # Create a progress bar
        pbar = tqdm(total=num_samples, desc="Generating files")
        
        # Create a callback to update the progress bar
        def update_progress(_):
            pbar.update(1)
        
        # Submit all tasks with the callback
        for size in sizes:
            pool.apply_async(gen_fn, (size,), callback=update_progress)
        
        pool.close()
        pool.join()
        pbar.close()


def _gen_filesizes(samples, min_size, max_size):
    # Generate power law distribution with a bias towards smaller files
    sizes = 1 - np.random.power(DEFAULT_ALPHA, size=samples)
    # Scale sizes to our desired range
    sizes = min_size + (max_size - min_size) * sizes
    return [int(s) for s in sizes]


def _generate_text_payload(size: int):
    """Helper function to generate a single text payload."""
    fake = Faker(use_weighting=USE_WEIGHTING)
    filename = f"{uuid.uuid4().hex[:10]}.txt"
    
    with open(filename, 'wb') as f:
        current_size = 0
        while current_size < size:
            # Generate and write chunks directly
            remaining = size - current_size
            chunk = fake.text(max_nb_chars=min(CHUNK_SIZE, remaining))
            chunk_bytes = chunk.encode('utf-8')
            f.write(chunk_bytes)
            current_size += len(chunk_bytes)


def _generate_binary_payload(size: int):
    """Helper function to generate a single binary payload."""
    fake = Faker(use_weighting=USE_WEIGHTING)
    filename = f"{uuid.uuid4().hex[:10]}.bin"
    
    with open(filename, 'wb') as f:
        current_size = 0
        while current_size < size:
            # Generate and write chunks directly
            remaining = size - current_size
            chunk = fake.binary(length=min(CHUNK_SIZE, remaining))
            f.write(chunk)
            current_size += len(chunk)


def _generate_json_payload(size: int):
    """Helper function to generate a single JSON payload."""
    fake = Faker(use_weighting=USE_WEIGHTING)
    filename = f"{uuid.uuid4().hex[:10]}.json"
    
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

    with open(filename, 'wb') as f:
        # Write the opening brace
        f.write(b'{')
        first_key = True
        current_size = 1  # Account for opening brace
        
        while current_size < size:
            # Generate a chunk of key-value pairs
            chunk = []
            chunk_size = 0
            
            # Build up a chunk of key-value pairs
            while chunk_size < CHUNK_SIZE and current_size + chunk_size < size:
                if not first_key:
                    chunk.append(b',')
                    chunk_size += 1
                first_key = False
                
                key = fake.word()
                value = generate_nested_value()
                kv_pair = f'"{key}":{json.dumps(value)}'.encode('utf-8')
                
                chunk.append(kv_pair)
                chunk_size += len(kv_pair)
            
            # Write the chunk
            f.write(b''.join(chunk))
            current_size += chunk_size
            
            # If we're close to the target size, break
            if current_size >= size - 100:  # Leave room for closing brace
                break
        
        # Write the closing brace
        f.write(b'}')
