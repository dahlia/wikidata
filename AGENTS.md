# Wikidata Python Client Library

## Build/Test Commands
- `uv sync`: Sync dependencies and create virtual environment
- `tox`: Run tests across all Python versions (3.8+, PyPy)
- `tox -e py311`: Run tests on specific Python version
- `uv run pytest tests/client_test.py::test_client_get -v`: Run single test
- `uv run mypy -p wikidata`: Type check main package
- `uv run flake8`: Lint code style
- `uv run sphinx-build docs/ docs/_build/html`: Build documentation

## Architecture
Python client library for Wikidata API. Core modules:
- `client.py`: Main Client class for API interactions
- `entity.py`: Entity data structures and types
- `cache.py`: Caching policies and implementation
- `datavalue.py`: Wikidata data value handling
- `multilingual.py`: Locale/language support
- `quantity.py`, `globecoordinate.py`, `commonsmedia.py`: Specialized data types

Uses urllib for HTTP requests, supports caching, fully typed with mypy.

## Code Style
- **Imports**: stdlib → third-party → local, sorted alphabetically
- **Types**: Strict mypy (check_untyped_defs=true, strict_optional=true)
- **Linting**: flake8 with spoqa import-order-style
- **Docstrings**: Detailed parameter documentation with types
- **Public API**: Use `__all__` for explicit exports
- **TYPE_CHECKING**: For conditional imports to avoid circular dependencies
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error handling**: Raise appropriate exceptions, log with logging module
