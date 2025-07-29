# Testing with VCR.py

This project uses VCR.py to record and replay HTTP interactions for testing without hitting the actual Sharp Cocoro API.

## Configuration

VCR.py is configured in `tests/conftest.py` with:
- Cassettes stored in `tests/cassettes/`
- Sensitive data filtering (appSecret, authorization headers)
- Recording mode set to "once" (records on first run, replays after)

## Writing Tests

Mark async tests that make HTTP calls with both decorators:
```python
@pytest.mark.asyncio
@pytest.mark.vcr
async def test_api_call():
    # Your test code
```

## Recording New Cassettes

1. Delete the existing cassette if re-recording:
   ```bash
   rm tests/cassettes/test_name.yaml
   ```

2. Run the test:
   ```bash
   uv run pytest tests/test_file.py::test_name -v
   ```

3. The cassette will be created automatically

## Running Tests

```bash
# Run all tests
just test

# Run specific test
uv run pytest tests/test_cocoro.py::test_login

# Run without recording (cassettes only)
uv run pytest --vcr-record=none
```