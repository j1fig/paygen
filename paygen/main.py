import typer
import uuid

from paygen import gen

app = typer.Typer()

@app.command()
def binary(samples: int, min_size: int = 100, max_size: int = 1000000):
    """Generate random binary payloads following a power law distribution"""
    payloads = gen.binary_payloads(samples, min_size, max_size)
    
    for payload in payloads:
        filename = f"{uuid.uuid4().hex[:10]}.bin"
        with open(filename, 'wb') as f:
            f.write(payload)

@app.command()
def json(samples: int, min_size: int = 100, max_size: int = 1000000):
    """Generate random JSON payloads following a power law distribution"""
    payloads = gen.json_payloads(samples, min_size, max_size)
    
    for payload in payloads:
        filename = f"{uuid.uuid4().hex[:10]}.json"
        with open(filename, 'wb') as f:
            f.write(payload)

@app.command()
def text(samples: int, min_size: int = 100, max_size: int = 1000000):
    """Generate random text payloads following a power law distribution"""
    payloads = gen.text_payloads(samples, min_size, max_size)
    
    for payload in payloads:
        filename = f"{uuid.uuid4().hex[:10]}.txt"
        with open(filename, 'wb') as f:
            f.write(payload)


if __name__ == "__main__":
    app()
