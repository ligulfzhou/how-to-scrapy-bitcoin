import sys
import time
import random
import asyncio
import logging
import binascii
import requests
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from aiorpcx import timeout_after, connect_rs
from pycoin.symbols.btc import network

logger = logging.getLogger("scrap_bitcoin_random")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler = RotatingFileHandler("log_scrap_bitcoin_random_%s.log" % (random.randint(100, 999)), maxBytes=104857600, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)

stderr = StreamHandler(sys.stderr)
stderr.setFormatter(formatter)
logger.addHandler(stderr)

filename = 'prikeys.txt'


class Bitcoin:

    def __init__(self, loop):
        self.loop = loop
        self.electrumx_host = 'localhost'
        self.electrumx_port = 8000
        self.storage_url = 'http://localhost:8080/save'

    def get_script(self, addr):
        return binascii.hexlify(network.parse.address(addr).script()).decode()

    async def get_bitcoin_balance(self, address, num):
        async with timeout_after(30):
            async with connect_rs(self.electrumx_host, self.electrumx_port) as session:
                script = self.get_script(address)
                session.transport._framer.max_size = 0
                result = await session.send_request('query', {'items': [script], 'limit': 1})
                logger.info("num: %s result: %s" % (num, result))
                if float(result[-1].strip('Balance:').strip('BTC')):
                    self.write_to_file([num])

                if result[1] != 'No history found':
                    print(f'save privatekey: {num} to storage service.....')
                    requests.post(self.storage_url, json={
                        'address': address,
                        'privkey': str(num)
                    })

    async def iterate_keys_of_num(self, num):
        key = network.keys.private(secret_exponent=num)
        public_pair = getattr(key, "public_pair", lambda: None)()
        if not public_pair:
            return

        for k, v, _ in network.output_for_public_pair(public_pair):
            if k not in ('address', 'address_uncompressed', 'address_segwit', 'p2sh_segwit'):
                continue

            while True:
                try:
                    await self.get_bitcoin_balance(v, num)
                    break
                except Exception as e:
                    logger.error('e: %s %s: %s' % (e, num, v))
                    time.sleep(5)

    def write_to_file(self, prikeys=[]):
        txt = ';'.join(prikeys)
        with open(filename, 'a') as f:
            f.writelines(txt+'\n')

    async def start_scrap(self):
        while True:
            num = random.randint(1, 115792089237316195423570985008687907853269984665640564039457584007913129639937)
            await self.iterate_keys_of_num(num)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    bitcoin = Bitcoin(loop)
    loop.run_until_complete(bitcoin.start_scrap())
    loop.close()

