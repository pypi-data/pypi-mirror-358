import base64
import json
import requests
from time import sleep
from .rest import BASE_DELAY, MAX_RETRIES, REQUEST_TIMEOUT, fetch_with_retry

def get_access_token(client_id, client_secret):
    auth_string = f"{client_id}:{client_secret}"
    auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": f"Basic {auth_base64}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.RequestException as e:
            delay = BASE_DELAY * (2 ** attempt)
            print(f"Error: token fetch attempt {attempt + 1} failed. Retrying in {delay}s... Error: {str(e)}")
            sleep(delay)
    
    print("Error: failed to obtain access token after retries")
    return None

def initialize_token_pool(credentials):
    tokens = [token for token in (
        get_access_token(*cred) for cred in credentials
    ) if token]
    
    if not tokens:
        print("No valid Spotify API tokens available")
        return None
    
    return tokens

def handel_response(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 5))
        print(f"Rate limited. Waiting {retry_after}s...")
        sleep(retry_after)
        return True
    else:
        return False

def search(token, query, **kwargs):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query}
    params.update(kwargs)
    data = fetch_with_retry(url, headers, params, handel_response)

    search_type = kwargs['type']
    if data and search_type + 's' in data:
        return [json.dumps(item) for item in data.get(search_type + 's', {}).get("items", [])]
    return []