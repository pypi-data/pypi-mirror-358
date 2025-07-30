import requests

API_URL = "https://lkteam-bancheck.deno.dev/checkban?uid={uid}"

def check_ban(uid: str):
    """
    Checks the ban status of a user ID using the lkteam-bancheck API.

    Args:
        uid (str): The user ID to check.

    Returns:
        dict: A dictionary containing the API response (e.g., uid, nickname, banned status).
              Returns an error dictionary if the request fails.
    """
    if not uid:
        return {"error": "UID cannot be empty."}

    try:
        # Format the URL with the provided UID
        url = API_URL.format(uid=uid)
        
        # Make the GET request
        response = requests.get(url, timeout=10) # 10-second timeout
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        # Parse the JSON response and return it
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}", "status_code": response.status_code}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"An error occurred with the request: {req_err}"}
    except ValueError: # Catches JSON decoding errors
        return {"error": "Failed to decode JSON from response."}