# PRS Commons

[![PyPI Version](https://img.shields.io/pypi/v/prs-commons.svg)](https://pypi.org/project/prs-commons/)
[![Python Versions](https://img.shields.io/pypi/pyversions/prs-commons.svg)](https://pypi.org/project/prs-commons/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/prs-commons/month)](https://pepy.tech/project/prs-commons)

A Python library containing common utilities and shared code for PRS microservices, including a high-level Odoo RPC client.

📖 [Documentation](https://ishafoundationit.github.io/prs-facade-common/) |
🐛 [Issue Tracker](https://github.com/IshaFoundationIT/prs-facade-common/issues) |
📦 [PyPI](https://pypi.org/project/prs-commons/)

## Features

- **AWS S3 Integration**: Async S3 client for file operations
- **PostgreSQL Client**: Async PostgreSQL client with connection pooling
- **Odoo RPC Client**: High-level client for interacting with Odoo's XML-RPC API
- **Type Annotations**: Full type hints for better IDE support
- **Environment Variable Support**: Easy configuration via `.env` files
- **Async/Await Support**: Built with modern Python async/await syntax

## Installation

### From PyPI (Recommended)

```bash
pip install prs-commons
```

### From Source (Development Only)

For development or contributing to the project:

For development, clone and install in editable mode:

```bash
git clone https://<token>@github.com/IshaFoundationIT/prs-facade-common.git
cd prs-facade-common
pip install -e ".[dev]"  # Install with development dependencies
```

### From Private Package Repository

Add your private package repository to pip configuration and install:

```bash
# Configure pip to use your private repository
pip config set global.extra-index-url https://your.private.registry.com/simple/

# Install the package
pip install prs-commons
```

## Quick Start

### Odoo RPC Client

```python
from prs_commons.odoo.rpc_client import OdooRPClient
from dotenv import load_dotenv

# Initialize the client (singleton)
client = OdooRPClient()

# Search for records
try:
    # Search for active partners
    domain = [('is_company', '=', True), ('active', '=', True)]
    fields = ['id', 'name', 'email']
    partners = client.search_read('res.partner', domain, fields=fields)

    # Create a new record
    new_partner_id = client.create_record('res.partner', {
        'name': 'John Doe',
        'email': 'john@example.com',
        'is_company': False
    })

    # Update a record
    client.write_record('res.partner', [new_partner_id], {
        'email': 'john.doe@example.com'
    })

except Exception as e:
    print(f"Error: {e}")
```

## Configuration

Create a `.env` file in your project root:

```env
ODOO_HOST=your-odoo-host.com
ODOO_DB=your_database
ODOO_LOGIN=your_email@example.com
ODOO_PASSWORD=your_password
```

## Documentation

For full documentation, please see the [API Reference](https://github.com/IshaFoundationIT/prs-facade-common#readme).

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## Development

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/) (recommended) or pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://<token>@github.com/IshaFoundationIT/prs-facade-common.git
   cd prs-facade-common
   ```

2. Install dependencies:
   ```bash
   # Using Poetry
   poetry install --with dev

   # Or using pip
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=prs_commons --cov-report=term-missing
```

## Publishing New Versions

### Prerequisites

1. Set up your `~/.pypirc` file with your GitHub token:
   ```ini
   [distutils]
   index-servers =
       github

   [github]
   repository = https://upload.pypi.org/legacy/
   username = __token__
   password = your_github_token_here
   ```

   Replace `your_github_token_here` with a GitHub Personal Access Token with `write:packages` scope.

2. Update the version in `pyproject.toml`

3. Build the package:
   ```bash
   python -m build
   ```

4. Publish to GitHub Package Registry:
   ```bash
   python -m twine upload --repository github dist/*
   ```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and pre-commit checks
4. Submit a pull request

## License

MIT
