# Proxy Manager

This script manages proxies by fetching them from specified URLs, validating them, and periodically updating the list of working proxies.

## Features
- Fetch proxies from a list of URLs
- Validate proxies and filter out non-working ones
- Support for different types of proxies: HTTP, SOCKS4, SOCKS5
- Fast mode for quick proxy validation
- Debug mode for detailed logging
- Scheduled fetching and validation

## Setup
1. Clone the repository:
    ```sh
    git clone https://github.com/Lucky7897/Get-free-proxies-that-work-automated.git
    ```
2. Install required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Run the script:
    ```sh
    python script.py
    ```

## Configuration
- `proxy.txt`: Add the URLs to fetch proxies from.
- `socks4_proxies.txt`: This file will store the fetched proxies.
- `invalid_urls.txt`: This file will store URLs that failed to fetch proxies.
- `proxy_stats.txt`: This file will store statistics about the fetched proxies.

## Usage
When running the script, you will be prompted to choose the type of proxies, mode, and whether to run in a loop.

## Author
- Lucky7897

[GitHub Repository](https://github.com/Lucky7897/Proxy-manager-)
