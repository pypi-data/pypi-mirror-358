# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

yutilx is a Python utilities library that provides the `CachedParallelProcessor` class for parallel processing with caching capabilities. The library uses MD5 hashing to cache results and ThreadPoolExecutor for concurrent execution.

## Development Commands

This project uses `uv` for dependency management and development workflow.

### Setup and Installation
```bash
# Clone and setup development environment
git clone https://github.com/cauyxy/yutilx.git
cd yutilx

# Install all dependencies (including dev dependencies)
uv sync

# Install in editable mode for development
uv pip install -e .
```

### Code Quality
```bash
# Format code with ruff
uv run ruff format

# Run linting checks
uv run ruff check

# Auto-fix linting issues
uv run ruff check --fix
```

### Testing
```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=yutilx
```

### Building
```bash
# Build distribution packages
uv build
```

### Publishing
Publishing to PyPI is automated via GitHub Actions when a release is created on GitHub.

## Architecture

### Project Structure
- `src/yutilx/` - Main package source code
  - `__init__.py` - Exports CachedParallelProcessor
  - `cached_parallel_processor.py` - Core implementation

### Key Components

**CachedParallelProcessor**: Main utility class that provides:
- Parallel processing of string inputs using ThreadPoolExecutor
- Automatic caching of results (file-based or in-memory)
- MD5 hashing for cache key generation
- Retry logic for failed processing attempts
- Progress tracking with tqdm

Usage pattern:
1. Initialize with a processing function
2. Call `run()` to process a list of inputs in parallel
3. Call `get_result()` to retrieve cached results

### Important Implementation Details

- Cache storage: JSONL format with structure `{"shash": "md5_hash", "result": "processed_result"}`
- Default cache filename: `cache.jsonl`
- File-free mode available for in-memory caching only
- Thread-safe cache operations
- Silent exception handling with retry mechanism

## Project Configuration

- Python version: >= 3.9
- Package manager: uv
- Linting/Formatting: ruff
- Testing framework: pytest (with coverage support)
- Build backend: hatchling