# PRS Commons

Welcome to the PRS Commons documentation!

## Overview

A Python library providing common utilities and integrations for the PRS system.

## Documentation

- [Odoo RPC Client](odoo) - High-level client for Odoo's XML-RPC API
- [Database Client](database) - Async PostgreSQL client with connection pooling
- [Storage Module](storage) - Unified interface for storage backends
- [AWS S3 Client](aws) - Thread-safe singleton client for AWS S3 storage operations


## Features

- **Odoo RPC Client**: A high-level client for interacting with Odoo's XML-RPC API
- **Database Client**: Asynchronous PostgreSQL client with connection pooling and transaction support
- **Storage Module**: Unified interface for interacting with different storage backends
  - Extensible base class for custom storage implementations
  - Built-in AWS S3 client
  - Consistent API across storage providers
- **AWS S3 Client**: Thread-safe singleton client for AWS S3 storage operations
  - File upload/download/delete
  - Pre-signed URL generation
  - Base64 encoding/decoding
- **Common Utilities**: Shared utilities and helpers for PRS services
- **Type Hints**: Full type annotations for better IDE support and code quality

## Installation

```bash
pip install prs-commons
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Table of Contents

```{toctree}
:maxdepth: 2
:caption: API Reference

odoo
database
storage
aws

```
