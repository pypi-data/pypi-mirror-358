# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **flex-evals** project, a Python implementation of the Flexible Evaluation Protocol (FEP) - a vendor-neutral, schema-driven standard for measuring the quality of any system that produces complex or variable outputs, particularly LLMs and agentic workflows.

### Key Architecture Components

- **Core Protocol**: Implements FEP schema-driven evaluation framework with test cases, outputs, checks, and results
- **Standard Checks**: Boolean, numeric, categorical, and free-text assessments using JSONPath expressions
- **Extended Checks**: LLM/agentic evaluations including semantic similarity and LLM judge checks
- **API Interface**: REST and gRPC APIs for running evaluations locally or at scale

### Dependencies

- Core: `jsonpath-ng`, `pydantic`, `python-dotenv`, `pyyaml`, `requests`, `ruamel-yaml`, `tenacity`, `tiktoken`
- Dev: `pytest`, `coverage`, `ruff`, `faker`, `pytest-asyncio`, `pytest-mock`, `pytest-timeout`

## Development Commands

### Build and Package
```bash
# Build package
make package-build

# Publish package (requires UV_PUBLISH_TOKEN)
make package-publish

# Full package workflow
make package
```

### Testing and Quality
```bash
# Run linting
make linting
# Equivalent to:
# uv run ruff check src/flex_evals/
# uv run ruff check tests/

# Run tests with coverage
make unittests
# Equivalent to:
# uv run coverage run -m pytest --durations=0 tests
# uv run coverage html

# Run all quality checks
make tests
```

### Package Management
```bash
# Add new dependency
uv add <package_name>

# Add dev dependency
uv add --dev <package_name>
```

## Test Configuration

- **Framework**: pytest with asyncio support
- **Test Path**: `tests/` directory
- **Python Path**: `src/` for imports
- **Timeout**: 60 seconds per test with signal method (Unix only)
- **Coverage**: HTML reports generated in `htmlcov/`

## Project Status

This appears to be an early-stage implementation of the FEP specification. The project structure is set up but the actual Python implementation files are not yet present in the `src/flex_evals/` directory.

## Important Notes

- Uses `uv` for dependency management and task running
- Follows FEP protocol specification (detailed in FEP.md)
- Designed for evaluating both deterministic and non-deterministic systems
- Supports JSONPath expressions for flexible data extraction
- Implements both synchronous and streaming evaluation interfaces