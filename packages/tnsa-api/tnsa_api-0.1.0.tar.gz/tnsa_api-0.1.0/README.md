# TNSA API SDK

This SDK provides a convenient way to interact with the TNSA API.

## Installation

```bash
pip install -e .
```

## Usage

```python
from tnsa_api import TNSAClient

client = TNSAClient(api_key="YOUR_API_KEY")

# List available models
models = client.list_models()
print(models)

# Get an inference from a model
inference = client.infer(
    model="NGen3.9-Lite-2006-Preview",
    prompt="Hello, world!"
)
print(inference)
```