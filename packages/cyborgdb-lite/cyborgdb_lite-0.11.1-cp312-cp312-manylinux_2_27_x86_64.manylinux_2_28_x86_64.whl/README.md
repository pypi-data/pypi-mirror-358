# CyborgDB Core

**CyborgDB** is the first Confidential Vector Database that enables you to ingest & search vectors emeddings in a privacy-preserving manner, without revealing the contents of the vectors themselves. It works with existing DBs (e.g., Postgres, Redis) and enables you to add, query and retrieve vector embeddings with transparent end-to-end encryption.

## Why Confidential?

According to KPMG, 63% of enterprises say that confidentiality and data privacy are their top risk to AI adoption. In regulated sectors, this figure increases to 76%. CyborgDB addresses these concerns with a novel approach to vector search that ensures your data remains secure.

## Key Features

- **End-to-End Encryption**: Vector embeddings remain encrypted throughout their lifecycle, including at search time
- **Zero-Trust Design**: Novel architecture keeps confidential inference data secure
- **High Performance**: GPU-accelerated indexing and retrieval with CUDA support
- **Familiar API**: Easy integration with existing AI workflows
- **Multiple Backing Stores**: Works with PostgreSQL, Redis, and in-memory storage
- **Cloud Ready**: Supports AWS RDS, AWS ElastiCache, Azure Database for PostgreSQL, Azure Cache for Redis, Google Cloud SQL, and Google Cloud Memorystore

## Installation

```bash
# Ensure Python 3.9 - 3.13 is installed
# You may want to create a virtual environment:
conda create -n cyborg-env python=3.12
conda activate cyborg-env

# Install CyborgDB Core:
pip install cyborgdb-core -i https://dl.cloudsmith.io/<token>/cyborg/cyborgdb/python/simple/
```

> **Note**: You will need to replace `<token>` with your token provided by Cyborg.

## Quickstart

```python
import cyborgdb_core as cyborgdb
import secrets

# Create a client with memory storage
# You can replace this with Postgres, Redis or another backing store
index_location = cyborgdb.DBConfig("memory")  # For index contents
config_location = cyborgdb.DBConfig("memory") # For config/loading
items_location = cyborgdb.DBConfig("memory")  # For item contents

# Create a client
client = cyborgdb.Client(index_location, config_location, items_location)

# Create an IVFFlat index
index_config = cyborgdb.IndexIVFFlat(dimension=4, n_lists=1024)

# Generate an encryption key for the index
index_key = secrets.token_bytes(32)

# Create an encrypted index
index = client.create_index("my_index", index_key, index_config)

# Add items to the encrypted index
items = [
    {"id": "item_1", "vector": [0.1, 0.2, 0.3, 0.4], "contents": "Hello!"},
    {"id": "item_2", "vector": [0.5, 0.6, 0.7, 0.8], "contents": "Bonjour!"},
    {"id": "item_3", "vector": [0.9, 0.10, 0.11, 0.12], "contents": "Hola!"}
]

index.upsert(items)

# Query the encrypted index
query_vector = [0.1, 0.2, 0.3, 0.4]
results = index.query(query_vector)

# Print the results
for result in results:
    print(f"ID: {result.id}, Distance: {result.distance}")
```

## Connecting to Different Backing Stores

### PostgreSQL

```python
index_location = cyborgdb.DBConfig(
    location="postgres",
    table_name="index_table", 
    connection_string="host=localhost dbname=cyborgdb user=postgres password=postgres"
)
```

### Redis

```python
index_location = cyborgdb.DBConfig(
    location="redis",
    connection_string="redis://localhost"
)
```

## Documentation

For more detailed documentation, visit:
- [CyborgDB Documentation](https://docs.cyborg.co)
- [API Reference](https://docs.cyborg.co/versions/v0.9.x/api-reference/python/introduction)

## System Requirements

- Python 3.9 - 3.13
- Operating Systems: Linux, macOS, or WSL
- For GPU acceleration: CUDA-compatible NVIDIA GPU

## License

CyborgDB Core is provided under a commercial license. Contact [Cyborg](https://www.cyborg.co/contact) for licensing information.

## About Cyborg

Cyborg is dedicated to making AI safe and secure. We develop solutions that enable organizations to leverage AI while maintaining the confidentiality and privacy of their data.

[Visit our website](https://www.cyborg.co) | [Contact Us](https://www.cyborg.co/contact)