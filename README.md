# Paygen
[![PyPI version](https://badge.fury.io/py/paygen.svg)](https://pypi.org/project/paygen/)


Paygen is a tool for generating random payloads for benchmarking and testing.

`paygen` supports generating a configurable number of payloads to files in the current directory.
The payloads themselves contain random data, with their sizes following a configurable power law distribution.

Right now, the only supported payload types are JSON, text, and binary.

This serves me in my benchmarking needs (to feed into the bench tool) - hoping it is useful for you.

## Installation

```bash
pip install paygen
```

## Usage

```bash
paygen --help
```