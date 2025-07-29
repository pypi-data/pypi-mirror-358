# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
A Python SDK for the Sharp Cocoro API, providing programmatic control of Sharp smart home devices (air conditioners and air purifiers). This is a Python port of the original TypeScript implementation.

## Development Commands

### Core Development Tasks
```bash
# Install dependencies
just install

# Run tests (currently no tests implemented)
just test

# Code quality checks
just lint          # Run ruff linter
just format        # Format code with ruff
just fix           # Auto-fix linting issues
just typecheck     # Run mypy type checker
just check         # Run all checks (lint + typecheck + test)

# Build and publish
just build         # Build distribution packages
just publish       # Publish to PyPI
just clean         # Clean build artifacts

# Dependency management
uv add <package>        # Add runtime dependency
uv add --dev <package>  # Add development dependency
uv sync                 # Sync dependencies from lock file
just info              # Show dependency tree
```

### Running Tests (when implemented)
```bash
# Run all tests
just test

# Run specific test file (future)
pytest tests/test_cocoro.py

# Run with coverage (future)
pytest --cov=sharp_cocoro
```

## Architecture Overview

### Core Components

1. **Main API Client** (`cocoro.py`)
   - `Cocoro` class: Async context manager handling authentication and API requests
   - Base URL: `https://hms.cloudlabs.sharp.co.jp/hems/pfApi/ta`
   - Key methods: `login()`, `query_devices()`, `execute_queued_updates()`, `fetch_device()`

2. **Device Hierarchy**
   ```
   Device (abstract base) → device.py
   ├── Aircon → devices/aircon/aircon.py
   ├── Purifier → devices/purifier/purifier.py
   └── UnknownDevice → devices/unknown.py
   ```

3. **Property System**
   - **SingleProperty**: Discrete values (ON/OFF, modes)
   - **RangeProperty**: Numeric ranges (temperature, humidity)
   - **BinaryProperty**: Binary data (complex states)
   - Properties can be readable (`get`), writable (`set`), or informational (`inf`)

4. **State Management**
   - Properties are queued locally before batch execution
   - `State8` class handles complex binary encoding for aircon features
   - All updates execute via `execute_queued_updates()` for efficiency

### Key Patterns

1. **Async/Await Throughout**
   ```python
   async with Cocoro(app_secret=secret, app_key=key) as cocoro:
       await cocoro.login()
       devices = await cocoro.query_devices()
   ```

2. **Property Queue Pattern**
   - Queue changes: `device.queue_temperature_update(23.5)`
   - Execute batch: `await cocoro.execute_queued_updates(device)`
   - Reduces API calls and ensures atomic updates

3. **Type Safety**
   - Extensive type hints with mypy checking
   - Enums for constants (StatusCode, ValueSingle)
   - Dataclasses for API responses

### Adding New Features

When adding device support:
1. Create new device class inheriting from `Device`
2. Define properties in a separate `*_properties.py` file
3. Implement device-specific queue methods
4. Add type to device factory in `cocoro.py`

When adding properties:
1. Define property structure (Single/Range/Binary)
2. Add to device's property collection
3. Implement queue method if writable
4. Update type hints

## Secret Management
```bash
# Store secrets with project prefix
chainenv update SHARPCOCORO_APP_SECRET 'your-secret'
chainenv update SHARPCOCORO_APP_KEY 'your-key'

# Use in .envrc
export APP_SECRET=$(chainenv get SHARPCOCORO_APP_SECRET)
export APP_KEY=$(chainenv get SHARPCOCORO_APP_KEY)
```

## Important Notes

- All API operations are asynchronous - use `async/await`
- Always use context manager for proper cleanup
- Queue multiple updates before executing for efficiency
- No retry logic implemented - handle failures in client code
- HTTP client is `httpx` with async support
- Project uses `uv` for package management, not Poetry
- Run `just check` before committing to ensure code quality