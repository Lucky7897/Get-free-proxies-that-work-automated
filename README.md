# Proxy Manager Script

## Overview

This Proxy Manager Script allows you to fetch and validate proxies from various URLs. It supports three modes: Fast, Normal, and Extensive Proxy Gathering. The script can also run in a loop with specified intervals, and it has a debug mode that provides detailed output about invalid URLs and proxy statistics.

## Features

- **Mode Selection**: Choose between Fast, Normal, and Extensive Proxy Gathering modes.
- **Fast Mode**: Fetch proxies from 5 URLs and find 50 working proxies.
- **Normal Mode**: Fetch proxies from 25 URLs.
- **Extensive Mode**: Fetch proxies from the entire list in `proxy.txt`.
- **Debug Mode**: Provides detailed output about invalid URLs and proxy statistics.
- **Output Formatting**: Ensures `IP:PORT` format and displays proxies with ping below 250 ms.
- **Loop Execution**: Option to run the script in a loop with user-defined intervals.
- **Automatic Execution**: Continues without freezing or requiring additional input.

## Installation

1. Clone the repository or download the script files.
2. Ensure you have Python installed (version 3.6 or higher).
3. Install the required Python packages using `pip`:

   
