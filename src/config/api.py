from config.settings import API_BASE_URL


class APIConfig:
    BASE_URL = API_BASE_URL

    HELLO = f"{BASE_URL}/hello"
    QUERY = f"{BASE_URL}/chat"
    CONNECT = f"{BASE_URL.replace('http', 'ws')}/connect"

