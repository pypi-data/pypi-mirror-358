import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DELAY = 1
MAX_RETRIES = 3
MAX_WORKERS = 100
REQUEST_TIMEOUT = 10

def fetch_with_retry(url, headers, params=None, block=None):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
            
            if block:
                should_continue = block(response)
                if should_continue:
                    continue
                
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            delay = BASE_DELAY * (2 ** attempt)
            print(f"Error: request failed (attempt {attempt + 1}). Retrying in {delay}s... Error: {str(e)}")
            time.sleep(delay)
    
    print(f"Error: failed after {MAX_RETRIES} attempts for URL: {url}, {params}")
    return None

def parallel_fetch(func, tokens, batches, **kwargs):
    results = []
    num_tokens = len(tokens)

    with ThreadPoolExecutor(max_workers=min(num_tokens, MAX_WORKERS)) as executor:
        futures = {
            executor.submit(func, tokens[i % num_tokens], batch, **kwargs): batch
            for i, batch in enumerate(batches)
        }

        for future in as_completed(futures):
            batch_result = future.result()
            if batch_result:
                results.extend(batch_result)

    return results