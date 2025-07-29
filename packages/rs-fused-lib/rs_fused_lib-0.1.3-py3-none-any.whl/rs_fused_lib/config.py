# rs_fused_lib/config.py
BASE_URL = "http://127.0.0.1:18001/api"

def set_base_url(url: str):
    global BASE_URL
    BASE_URL = url

def get_base_url() -> str:
    return BASE_URL 