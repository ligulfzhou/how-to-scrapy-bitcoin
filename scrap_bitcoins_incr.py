import sys
import json
import random
import socket
import asyncio
import logging
import hashlib
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from aiorpcx import timeout_after, connect_rs
import electrumx.lib.text as text

from pycoin.symbols.btc import network
from electrum.bitcoin import address_to_scripthash

logger = logging.getLogger("scrap_bitcoin")
logger.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler = RotatingFileHandler("log_scrap_bitcoin.log", maxBytes=104857600, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)

stderr = StreamHandler(sys.stderr)
stderr.setFormatter(formatter)
logger.addHandler(stderr)


indexname = 'indext'
filename = 'prikeys.txt'


class Bitcoin:

    def __init__(self, loop):
        self.loop = loop
        self.electrumx_host = 'localhost'
        self.electrumx_port = 8000
        self.index = self.load_index()

    def load_index(self):
        try:
            with open(indexname, 'r') as f:
                return int(f.read())
        except:
            return 1

    def set_index(self, index):
        with open(indexname, 'w') as f:
            f.write(index)

    async def get_bitcoin_balance(self, scripthash, num):
        async with timeout_after(30):
            async with connect_rs(self.electrumx_host, self.electrumx_port) as session:
                session.transport._framer.max_size = 0
                result = await session.send_request('query', {'items': [scripthash], 'limit': 1})
                logger.info("num: %s result: %s" % (num, result))
                if float(result[-1].strip('Balance:').strip('BTC')):
                    self.write_to_file([num])

    async def iterate_keys_of_num(self, num):
        res = []
        key = network.keys.private(secret_exponent=num)
        public_pair = getattr(key, "public_pair", lambda: None)()
        if not public_pair:
            return

        scripthashes = []
        for k, v, text in network.output_for_public_pair(public_pair):
            if k not in ('address', 'address_uncompressed', 'address_segwit', 'p2sh_segwit'):
                continue

            try:
                sh = address_to_scripthash(v)
                scripthashes.append(sh)
            except Exception as e:
                logger.error(e)
                continue

        for scripthash in scripthashes:
            try:
                await self.get_bitcoin_balance(scripthash, num)
            except Exception as e:
                logger.error('e: %s %s: %s'%(e, num, scripthash))

    def write_to_file(self, prikeys=[]):
        txt = ';'.join(prikeys)
        with open(filename, 'a') as f:
            f.writelines(txt+'\n')

    async def start_scrap(self):
        while True:
            await self.iterate_keys_of_num(self.index)
            self.index += 1
            if not self.index % 100:
                self.set_index(self.index)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    bitcoin = Bitcoin(loop)
    loop.run_until_complete(bitcoin.start_scrap())
    loop.close()

