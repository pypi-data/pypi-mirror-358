# Proxar

Proxar is a Python client for fetching public proxies from various online sources.

It uses an asynchronous architecture to retrieve fresh proxies from multiple providers, providing a stream of proxies for use in web scraping, data analysis, and other network-intensive tasks.

---

## Features

- **Multi-Source Proxy Fetching:** Retrieves proxies from several providers.
- **Asynchronous Architecture:** Built entirely on `asyncio` and `aiohttp` for efficient, non-blocking network operations.
- **Platform-Aware Storage:** Uses `platformdirs` to store proxies in the appropriate user-specific data directory on any OS, with an option for users to specify a custom path.
- **Simple Text-Based Storage:** Saves proxies to simple `.txt` files, making them easy to read, parse, and share.
- **Configurable Logging:** Provides detailed logging for monitoring and debugging.

---

## Installation

### From PyPI (Recommended)

```bash
pip install proxar
```

### From Source

You can set up Proxar by cloning the repository directly.

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/proxar.git
    cd proxar
    ```
2.  Install the project and its dependencies:
    ```bash
    pip install -e .
    ```
    - To install development dependencies like `mypy` and `ruff`, use:
    ```bash
    pip install -e .[dev]
    ```

---

## Usage

Here’s a basic example of how to use Proxar to fetch proxies:

```python
import asyncio
from proxar import Proxar

async def main():
    # Initialize Proxar
    # You can optionally provide a custom storage path:
    # proxar = Proxar(storage_path="/path/to/your/proxies")
    proxar = Proxar()

    try:
        # Fetch proxies from all configured sources
        await proxar.get_proxies()
        print("Proxy fetching complete.")
        print(f"Proxies saved to: {proxar.storage_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Configuration

Proxar is designed to work out-of-the-box with minimal configuration.

-   **Storage:** By default, Proxar stores fetched proxies in a `proxar` directory inside your user data folder. You can override this by passing a `storage_path` argument during initialization.
-   **Logging:** Logging levels and output can be configured within the library's logging module.

---

## Dependencies

All project dependencies are managed via [`pyproject.toml`](pyproject.toml).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions, bug reports, and feature requests are welcome!
Please open an issue or submit a pull request on [GitHub](https://github.com/filming/proxar).
