import requests
import time
from datetime import datetime, timedelta
from threading import Timer
import sys
import os
import concurrent.futures
import random
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("proxy_manager.log", encoding='utf-8'), logging.StreamHandler()]
)

# File paths
proxy_list_file = "proxy.txt"
fetched_proxies_file = "fetched_proxies.txt"
validation_output_file_prefix = "validated_working_proxies"
invalid_urls_file = "invalid_urls.txt"
proxy_stats_file = "proxy_stats.txt"
hundred_working_results_file_prefix = "100_working_results"
invalid_url_backups_file = "invalid_url_backups.txt"

def fetch_proxies(proxy_type, max_urls, fast_mode=False, debug_mode=False):
    all_proxies = set()
    invalid_urls = []
    proxy_stats = {}
    urls_to_remove = []
    start_time = time.time()

    # Read proxy URLs from proxy_list_file
    try:
        with open(proxy_list_file, 'r') as file:
            proxy_sources = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"{proxy_list_file} not found.")
        return []

    logging.info("Starting to fetch proxies.")
    for url in proxy_sources:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            proxies = response.text.splitlines()
            for proxy in proxies:
                if proxy_type.lower() in ['http', 'socks4', 'socks5'] and proxy.count(':') == 1:
                    all_proxies.add(proxy)
            proxy_count = len(proxies)
            proxy_stats[url] = proxy_count
            if proxy_count < 50:
                urls_to_remove.append(url)
            logging.info(f"Fetched proxies from {url} with {proxy_count} proxies.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch from {url}: {e}")
            invalid_urls.append(url)

    if fast_mode:
        all_proxies = list(all_proxies)[:50]

    with open(fetched_proxies_file, 'w', encoding='utf-8') as file:
        file.write("\n".join(all_proxies) + "\n")

    end_time = time.time()
    logging.info(f"Total unique proxies fetched: {len(all_proxies)}")
    logging.info(f"Total invalid URLs: {len(invalid_urls)}")
    logging.info(f"Total time taken: {end_time - start_time:.2f} seconds")

    if debug_mode:
        with open(invalid_urls_file, 'w', encoding='utf-8') as file:
            file.write("\n".join(invalid_urls) + "\n")
        with open(proxy_stats_file, 'w', encoding='utf-8') as file:
            for url, count in proxy_stats.items():
                file.write(f"{url}: {count} proxies\n")
        logging.info(f"Invalid URLs saved to {invalid_urls_file}")
        logging.info(f"Proxy stats saved to {proxy_stats_file}")

    handle_invalid_urls(proxy_sources, invalid_urls + urls_to_remove)
    return list(all_proxies)

def handle_invalid_urls(all_urls, invalid_urls):
    with open(invalid_url_backups_file, 'w', encoding='utf-8') as backup_file:
        backup_file.write("\n".join(invalid_urls) + "\n")
    
    valid_urls = [url for url in all_urls if url not in invalid_urls]
    with open(proxy_list_file, 'w', encoding='utf-8') as url_file:
        url_file.write("\n".join(valid_urls) + "\n")
    
    logging.info(f"Invalid URLs backed up to {invalid_url_backups_file} and removed from {proxy_list_file}")

def validate_proxy(proxy):
    try:
        start = time.time()
        response = requests.get("http://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
        end = time.time()
        ping = (end - start) * 1000  # Convert to milliseconds
        return (proxy, ping) if response.status_code == 200 and ping < 250 else None
    except:
        return None

def validate_proxies(fast_mode=False):
    with open(fetched_proxies_file, 'r', encoding='utf-8') as file:
        proxies = [line.strip() for line in file]

    if fast_mode:
        proxies = proxies[:50]

    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(validate_proxy, proxy) for proxy in proxies]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                working_proxies.append(result)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H")
    output_file = f"{validation_output_file_prefix}_{timestamp}.txt"
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("\n".join(proxy for proxy, _ in working_proxies) + "\n")

    logging.info(f"Validation complete. Working proxies saved to {output_file}")
    logging.info("Suggested fast working proxies with ping below 250 ms:")
    for proxy, ping in working_proxies:
        logging.info(f"{proxy} - {ping:.2f} ms")

def fetch_and_validate_proxies_until_100(proxy_type, max_urls, debug_mode=False):
    all_proxies = set()
    working_proxies = []
    urls = []

    try:
        with open(proxy_list_file, 'r', encoding='utf-8') as url_file:
            urls = [line.strip() for line in url_file if line.strip()]
    except FileNotFoundError:
        logging.error(f"{proxy_list_file} not found.")
        return

    while len(working_proxies) < 100:
        if not urls:
            logging.warning("No more URLs to fetch from.")
            break

        url = random.choice(urls)
        logging.info(f"Fetching proxies from {url}...")
        fetched_proxies = fetch_proxies(proxy_type, max_urls, debug_mode=debug_mode)
        all_proxies.update(fetched_proxies)

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(validate_proxy, proxy) for proxy in fetched_proxies]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    working_proxies.append(result)
        
        if len(working_proxies) >= 100:
            break

        urls.remove(url)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H")
    output_file = f"{hundred_working_results_file_prefix}_{timestamp}.txt"
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("\n".join(proxy for proxy, _ in working_proxies) + "\n")

    logging.info(f"100 Working Proxies result saved to {output_file}")

def status_update(next_fetch, next_validate):
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sys.stdout.write(f"\r[{now}] The script is currently still functional. Next fetch: {next_fetch}, Next validate: {next_validate}")
        sys.stdout.flush()
        time.sleep(10)

def start_timed_execution(fetch_interval, validate_interval, proxy_type, max_urls, fast_mode, debug_mode):
    fetch_proxies(proxy_type, max_urls, fast_mode, debug_mode)
    validate_proxies(fast_mode)

    next_fetch = datetime.now() + timedelta(minutes=fetch_interval)
    next_validate = datetime.now() + timedelta(minutes=validate_interval)

    fetch_timer = Timer(fetch_interval * 60, fetch_proxies, [proxy_type, max_urls, fast_mode, debug_mode])
    validate_timer = Timer(validate_interval * 60, validate_proxies, [fast_mode])
    
    fetch_timer.start()
    validate_timer.start()

    try:
        status_update(next_fetch.strftime("%Y-%m-%d %H:%M:%S"), next_validate.strftime("%Y-%m-%d %H:%M:%S"))
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
        fetch_timer.cancel()
        validate_timer.cancel()

def main():
    logging.info("Select proxy type:")
    logging.info("1: SOCKS4")
    logging.info("2: SOCKS5")

    proxy_type_input = int(input("Enter proxy type (1 or 2): "))
    proxy_type_map = {1: "socks4", 2: "socks5"}
    proxy_type = proxy_type_map.get(proxy_type_input)

    if proxy_type not in proxy_type_map.values():
        logging.error("Invalid proxy type. Exiting.")
        return

    logging.info("Select mode:")
    logging.info("1: Fast (fetch from 5 URLs, find 50 working proxies)")
    logging.info("2: Normal (fetch from 25 URLs)")
    logging.info("3: Extensive Proxy Gathering (fetch from entire list in proxy.txt)")
    logging.info("4: 100 Working Mode (fetch up to 100 working proxies)")

    mode_input = int(input("Enter mode (1, 2, 3, 4): "))
    if mode_input == 1:
        mode = "fast"
        max_urls = 5
        logging.info("FAST mode selected. Only fetching 50 functional proxies.")
    elif mode_input == 2:
        mode = "normal"
        max_urls = 25
    elif mode_input == 3:
        mode = "extensive"
        max_urls = None
    elif mode_input == 4:
        mode = "100_working"
        max_urls = 1000
    else:
        logging.error("Invalid mode. Exiting.")
        return

    debug_mode_input = input("Do you want to run in debug mode? (y/n): ").strip().lower()
    debug_mode = debug_mode_input == 'y'

    if mode == "100_working":
        fetch_and_validate_proxies_until_100(proxy_type, max_urls, debug_mode)
    else:
        run_in_loop = input("Do you want to run the scripts in a loop? (y/n): ").strip().lower()
        if run_in_loop == 'y':
            fetch_interval = int(input("Enter the interval (in minutes) for fetching proxies: "))
            validate_interval = int(input("Enter the interval (in minutes) for validating proxies: "))
            start_timed_execution(max(20, fetch_interval), max(20, validate_interval), proxy_type, max_urls, mode == "fast", debug_mode)
        elif run_in_loop == 'n':
            fetch_proxies(proxy_type, max_urls, mode == "fast", debug_mode)
            validate_proxies(mode == "fast")
        else:
            logging.error("Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()
