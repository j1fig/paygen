# Paygen

Paygen is a tool for generating random payloads for bechmarking and testing.

`paygen` supports generating a configurable number of payloads to files in the current directory, or to stdout.
The payloads themselves contain random data, with their sizes following a configurable power law distribution.

Right now, the only supported payload types are JSON, text, and binary.

## Installation

```bash
pip install paygen
```

## Usage

```bash
paygen --help
```