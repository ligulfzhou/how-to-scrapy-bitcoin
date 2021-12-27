import sys
import asyncio
import logging
import binascii
import time
import argparse
import requests

from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from aiorpcx import timeout_after, connect_rs
from pycoin.symbols.btc import network
from utils import save_private_key, address_to_script


logger = logging.getLogger("scrap_bitcoin_incr")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler = RotatingFileHandler("log_scrap_bitcoin_incr.log", maxBytes=104857600, backupCount=1)
handler.setFormatter(formatter)
logger.addHandler(handler)

stderr = StreamHandler(sys.stderr)
stderr.setFormatter(formatter)
logger.addHandler(stderr)

indexname = 'index'
filename = 'prikeys.txt'


class Bitcoin:

    def __init__(self, loop, idx):
        self.process_idx = idx
        self.loop = loop
        self.electrumx_host = 'localhost'
        self.electrumx_port = 8000
        self.index = self.load_index()

    def load_index(self):
        try:
            with open(f'{indexname}{self.process_idx}', 'r') as f:
                return int(f.read())
        except:
            return 1

    def set_index(self, index):
        with open(f'{indexname}{self.process_idx}', 'w') as f:
            f.write(str(index))

    async def get_bitcoin_balance(self, address, num):
        async with timeout_after(30):
            async with connect_rs(self.electrumx_host, self.electrumx_port) as session:
                script = address_to_script(address)
                session.transport._framer.max_size = 0
                result = await session.send_request('query', {'items': [script], 'limit': 1})
                logger.info("num: %s result: %s" % (num, result))
                if float(result[-1].strip('Balance:').strip('BTC')):
                    self.write_to_file([num])

                if result[1] != 'No history found':
                    print(f'save privatekey: {num} to storage service.....')
                    try:
                        save_private_key('', address, str(num))
                    except:
                        pass

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
            f.writelines(txt + '\n')

    async def start_scrap(self):
        while True:
            await self.iterate_keys_of_num(self.index)
            self.index += 1
            if not self.index % 100:
                self.set_index(self.index)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='update hostname and control telegraf')
    parser.add_argument('--idx', type=int, default=1, help='process N')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    bitcoin = Bitcoin(loop, args.idx)
    loop.run_until_complete(bitcoin.start_scrap())
    loop.close()
