# norsulabs-sdk

A Python SDK for NorsuLabs.

# Installation

```bash
pip install norsulabs
```

# Usage

```python
from norsulabs.client import NorsuLabsClient

client = NorsuLabsClient(api_key="your-api-key",deployment_id="your-deployment-id")

client.inference(input_data)

```