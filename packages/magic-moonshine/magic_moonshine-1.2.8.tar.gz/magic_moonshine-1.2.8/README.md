# Moonshine API Client

A Python client for interacting with the Moonshine Edge Compute API.

## Installation

```bash
pip install magic-moonshine
```

## Usage

```python
import moonshine

# Configure your API token
moonshine.config(API="your-api-token")

# Search in a bucket
results = moonshine.search(bucket="your-bucket-id", query="your search query")
print(results)
```
