# Xify

Xify is a modern, asynchronous Python client for interacting with the X (formerly Twitter) API.

It provides authentication, error handling, and a clean async interface for common tasks.

---

## Features

- **OAuth 1.0a Authentication:** Sign and authenticate requests to the X API.
- **Async HTTP Requests:** Uses `aiohttp` for efficient, non-blocking network operations.
- **Custom Error Handling:** Clear exception hierarchy for all error cases.
- **Logging:** Built-in logging with easy integration into your application’s logging setup.
- **Example Usage:** See [`examples`](examples) for working scripts.

---

## Installation

You can install Xify from source or from PyPI.

### From Source

```bash
git clone https://github.com/filming/xify.git
cd xify
pip install -e .[dev]
```
- The `[dev]` extra will install development dependencies like `mypy` and `ruff`.

### From PyPI

```bash
pip install xify
```

---

## Usage

Here’s a minimal example for posting a tweet:

```python
import asyncio
import os
import logging
from dotenv import load_dotenv
from xify import Xify
from xify.errors import APIError, XifyError

load_dotenv()

# Configure logging to see output from Xify
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

async def main():
    try:
        xify_client = Xify(
            consumer_key=os.getenv("CONSUMER_KEY"),
            consumer_secret=os.getenv("CONSUMER_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"),
            access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
        )
        async with xify_client:
            content = {"msg": "Hello X!"}
            response = await xify_client.tweet(content)
        logging.info("Tweet posted successfully! ID: %s", response["id"])
    except APIError as e:
        logging.error("API error: %s", e)
        logging.error("Full error response from API: %s", e.response)
    except XifyError as e:
        logging.error("A library error occurred: %s", e)
    except Exception:
        logging.exception("An unexpected error occurred.")

if __name__ == "__main__":
    asyncio.run(main())
```

See [`examples`](examples) for ready-to-run scripts.

---

## Configuration

Xify requires four credentials to authenticate with the X API:

- `consumer_key`
- `consumer_secret`
- `access_token`
- `access_token_secret`

You can provide these credentials to the `Xify` initializer in any way you prefer—such as reading from environment variables, a `.env` file, a configuration file, a database, or any other method.

**Example using environment variables:**

Set your environment variables in your shell (for example, in `.bashrc`, `.zshrc`, or directly in your terminal):

```bash
export CONSUMER_KEY="your_consumer_key"
export CONSUMER_SECRET="your_consumer_secret"
export ACCESS_TOKEN="your_access_token"
export ACCESS_TOKEN_SECRET="your_access_token_secret"
```

Then, in your code:

```python
import os
from xify import Xify

xify_client = Xify(
    consumer_key=os.getenv("CONSUMER_KEY"),
    consumer_secret=os.getenv("CONSUMER_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)
```

---

## Error Handling

Xify provides a robust error hierarchy:

- `XifyError`: Base class for all library errors.
- `AuthError`: Raised for authentication issues.
- `APIError`: Raised for errors returned by the X API (includes the full API response in `.response`).
- `RequestError`: Raised for network or request issues.

You should catch these exceptions in your application for consistent error handling.

---

## Logging

- Xify uses Python’s standard `logging` library.
- By default, it adds a `NullHandler` to prevent "No handler found" warnings if you have not set up logging in your application.
---

## Dependencies

All dependencies are managed via [`pyproject.toml`](pyproject.toml).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions, bug reports, and feature requests are welcome!  
Please open an issue or submit a pull request on [GitHub](https://github.com/filming/xify).
