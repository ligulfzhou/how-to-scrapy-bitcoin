import time
import requests
from functools import wraps


def retry(cnt: int = 3):
    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            for i in range(cnt):
                try:
                    return method(*args, **kwargs)
                except Exception as e:
                    print('run %s failed with %s' % (method.__name__, e))
                    time.sleep(5 * (i + 1))
                raise
        return wrapper
    return decorator


@retry(cnt=3)
def fetch_api(url: str, method: str = 'GET', headers: dict = {}, params: dict = {}, body: dict = {}, data: dict = {},
               raw: bool = False):
    if method == 'GET':
        res = requests.get(url, headers=headers, params=params)
    else:
        res = requests.post(url, json=body, headers=headers, params=params, data=data)

    if raw:
        return res.text
    else:
        return res.json()
