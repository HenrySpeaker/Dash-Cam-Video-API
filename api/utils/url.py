import requests


def verify_youtube_url(url):
    """
    Returns True if youtube video get is successful from given URL, otherwise False.
    """
    try:
        response = requests.get(url)
        return response.status_code >= 200 and response.status_code <= 299

    except requests.ConnectionError:
        return False
