import asyncio
import socket
import random
import logging
import logging.config
import json
import redis
import plyvel

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')


filename = 'prikeys.txt'


class DB(object):

    def __init__(self):
        self.db = plyvel.DB('/root/addr2priv', create_if_missing=True)

    def get(self, key, default=b''):
        v = self.db.get(key.encode(), default)
        return v

    def get_multi(self, keys):
        res = {key: self.get(key, '') for key in keys}
        return res

    def put(self, k, v):
        self.db.put(k.encode(), v.encode())

    def put_multi(self, kv):
        assert isinstance(kv, dict) and kv
        with self.db.write_batch() as wb:
            for k, v in kv.items():
                wb.put(k.encode(), v.encode())

db = DB()


class MyProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        try:
            data = json.loads(data.decode())
            print('data received {}'.format(data))

            method, params = data['method'], data['params']
            if method == 'put_multi':
                db.put_multi(params[0])
            elif method == 'get_multi':
                res = db.get_multi(params[0])
                self.transport.write(json.dumps(res).encode()+b'\n')
                logger.error('sent: {}'.format(json.dumps(res).encode()+b'\n'))
            else:
                pass
        except Exception as e:
            logger.error('error: {}'.format(e))

        self.transport.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = loop.create_server(MyProtocol, '127.0.0.1', 50005)
    server = loop.run_until_complete(coro)

    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

