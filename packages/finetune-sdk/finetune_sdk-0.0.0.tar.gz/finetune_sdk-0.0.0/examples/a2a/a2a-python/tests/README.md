## Running the tests

1. Run the tests
    ```bash
    uv run pytest -v -s client/test_client.py
    ```

In case of failures, you can cleanup the cache:

1. `uv clean`
2. `rm -fR .pytest_cache .venv __pycache__`
