import os

import redis

host = os.environ.get('host', '')
port = os.environ.get('port', 6379)
password = os.environ.get('password', '')
rs = redis.Redis(host=host, port=port, password=password)


def main():
    pass


if __name__ == '__main__':
    main()