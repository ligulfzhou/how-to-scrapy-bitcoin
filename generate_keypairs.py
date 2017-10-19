import socket
import time
import json
import random
import os
import pycoin
import asyncio
from pycoin.key.Key import Key
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')


filename = 'prikeys.txt'

class Bitcoin:

    def __init__(self, loop):
        self.loop = loop
        self.leveldb_host = '127.0.0.1'
        self.leveldb_port = 50005

    async def _send_addr_priv(self, pairs):
        reader, writer = await asyncio.open_connection(self.leveldb_host, self.leveldb_port, loop=self.loop)
        data = {
            'params': [pairs],
            'method': 'put_multi'
        }
        writer.write(json.dumps(data).encode())
        logger.info('send pairs, {}'.format(pairs))
        writer.close()

    async def generate_keypairs(self, num):
        pairs = {}
        for i in range(num, num+128):
            k = Key(i)
            addr, priv = k.address(), k.wif()
            addr2, priv2 = k.address(use_uncompressed=True), k.wif(use_uncompressed=True)
            pairs.update({
                addr: priv,
                addr2: priv2
            })

        await self._send_addr_priv(pairs)

    async def start_scrap(self):
        while True:
            num = random.randint(1, 115792089237316195423570985008687907853269984665640564039457584007913129639937-128)
            logger.info('No: {}'.format(num))
            await self.generate_keypairs(num)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    bitcoin = Bitcoin(loop)
    loop.run_until_complete(bitcoin.start_scrap())
    loop.close()

