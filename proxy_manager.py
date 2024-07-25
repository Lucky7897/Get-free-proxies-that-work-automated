import requests
import time
from datetime import datetime, timedelta
from threading import Timer
import sys
import os
import concurrent.futures

# File paths
proxy_list_file = "proxy.txt"
fetched_proxies_file = "socks4_proxies.txt"
validation_output_file_prefix = "validated_working_proxies"
invalid_urls_file = "invalid_urls.txt"
proxy_stats_file = "proxy_stats.txt"

def fetch_proxies(proxy_type, max_urls, fast_mode=False, debug_mode=False):
    all_proxies = set()
    invalid_urls = []
    proxy_stats = {}
    start_time = time.time()
    
    with open(proxy_list_file, 'r') as url_file:
        urls = url_file.readlines()
    
    if max_urls:
        urls = urls[:max_urls]
    
    for url in urls:
        url = url.strip()
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            proxies = response.text.splitlines()
            for proxy in proxies:
                if proxy_type.lower() in ['http', 'socks4', 'socks5'] and proxy.count(':') == 1:
                    all_proxies.add(proxy)
            proxy_stats[url] = len(proxies)
            print(f"Fetched proxies from {url}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch from {url}: {e}")
            invalid_urls.append(url)
    
    # Adjust the number of proxies for fast mode
    if fast_mode:
        all_proxies = list(all_proxies)[:50]
    
    with open(fetched_proxies_file, 'w') as file:
        for proxy in all_proxies:
            file.write(proxy + "\n")
    
    end_time = time.time()
    total_time = end_time - start_time
    total_proxies = len(all_proxies)
    
    print(f"\nTotal unique proxies fetched: {total_proxies}")
    print(f"Total invalid URLs: {len(invalid_urls)}")
    print(f"Total time taken: {total_time:.2f} seconds")
    
    if debug_mode:
        with open(invalid_urls_file, 'w') as file:
            for url in invalid_urls:
                file.write(url + "\n")
        with open(proxy_stats_file, 'w') as file:
            for url, count in proxy_stats.items():
                file.write(f"{url}: {count} proxies\n")
        
        print(f"Invalid URLs saved to {invalid_urls_file}")
        print(f"Proxy stats saved to {proxy_stats_file}")
    
    return list(all_proxies)

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
    with open(fetched_proxies_file, 'r') as file:
        proxies = file.readlines()
    
    if fast_mode:
        proxies = proxies[:50]
    
    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(validate_proxy, proxy.strip()) for proxy in proxies]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                working_proxies.append(result)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H")
    output_file = f"{validation_output_file_prefix}_{timestamp}.txt"
    
    with open(output_file, 'w') as file:
        for proxy, ping in working_proxies:
            file.write(f"{proxy}\n")
    
    print(f"\nValidation complete. Working proxies saved to {output_file}")
    print("\nSUGGESTED FAST WORKING PROXIES WITH PING BELOW 250 MS")
    for proxy, ping in working_proxies:
        print(proxy)

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
        print("\nStopping execution...")
        fetch_timer.cancel()
        validate_timer.cancel()

def main():
    if not os.path.exists(proxy_list_file):
        with open(proxy_list_file, 'w') as file:
            print(f"{proxy_list_file} not found. Please populate it with proxy URLs.")
            file.write("https://www.proxy-list.download/api/v1/get?type=socks4\n")  # example entry
            print(f"{proxy_list_file} created. Please populate it with proxy URLs in the needed format.")
        return
    
    print("Welcome to the Proxy Manager.")
    proxy_type_input = int(input("Enter the type of proxies to fetch (1 for http, 2 for socks4, 3 for socks5): "))
    proxy_type_map = {1: "http", 2: "socks4", 3: "socks5"}
    proxy_type = proxy_type_map.get(proxy_type_input)
    if proxy_type not in proxy_type_map.values():
        print("Invalid proxy type. Exiting.")
        return
    
    print("Select mode:")
    print("1: Fast (fetch from 100 URLs, find 50 working proxies)")
    print("2: Normal (fetch from 1000 URLs)")
    print("3: Extensive Proxy Gathering (fetch from entire list in proxy.txt)")
    print("4: Extreme (fetch from all available URLs in proxy.txt)")
    mode_input = int(input("Enter mode (1, 2, 3, 4): "))
    
    if mode_input == 1:
        mode = "fast"
        max_urls = 100
        print("FAST mode selected. Fetching 100 URLs and finding 50 functional proxies.")
    elif mode_input == 2:
        mode = "normal"
        max_urls = 1000
    elif mode_input == 3:
        mode = "extensive"
        max_urls = None  # Fetch from entire list
    elif mode_input == 4:
        mode = "extreme"
        max_urls = None  # Fetch from entire list
    else:
        print("Invalid mode. Exiting.")
        return
    
    debug_mode_input = input("Do you want to run in debug mode? (y/n): ").strip().lower()
    debug_mode = True if debug_mode_input == 'y' else False
    
    run_in_loop = input("Do you want to run the scripts in a loop? (y/n): ").strip().lower()
    if run_in_loop == 'y':
        fetch_interval = int(input("Enter the interval (in minutes) for fetching proxies: "))
        validate_interval = int(input("Enter the interval (in minutes) for validating proxies: "))
        start_timed_execution(fetch_interval, validate_interval, proxy_type, max_urls, mode == "fast", debug_mode)
    elif run_in_loop == 'n':
        fetch_proxies(proxy_type, max_urls, mode == "fast", debug_mode)
        validate_proxies(mode == "fast")
    else:
        print("Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()