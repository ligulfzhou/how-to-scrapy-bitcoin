import os

import redis

host = os.environ.get('host', '45.76.69.116')
port = os.environ.get('port', 6379)
password = os.environ.get('password', 'REDISzlg153')
rs = redis.Redis(host=host, port=port, password=password)
