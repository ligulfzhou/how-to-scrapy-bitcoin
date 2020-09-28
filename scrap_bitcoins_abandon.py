import pdb
import socket
import argparse
import hashlib
import time
import errno
import json
import random
import os
import pycoin
import asyncio
import logging
import logging.config
from pycoin.symbols.btc import network

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')


filename = 'prikeys.txt'

class Bitcoin:

    def __init__(self, loop):
        self.loop = loop
        self.electrumx_host = '127.0.0.1'
        self.electrumx_port = 50001
        self.leveldb_host = '127.0.0.1'
        self.leveldb_port = 50005

    async def get_bitcoin_balance(self, addr):
        reader, writer = await asyncio.open_connection(self.electrumx_host, self.electrumx_port, loop=self.loop)
        params = {
            'jsonrpc': '2.0',
            'method': 'blockchain.scripthash.get_balance',
            'params': [addr],
            'id': addr
        }
        writer.write(json.dumps(params).encode()+b'\n')
        logger.info('data send')
        data = await reader.read(1024)
        writer.close()
        logger.error('bitcoin_balace: {}'.format(json.loads(data)))
        data = json.loads(data)
        res = {
            'confirmed': data['result']['confirmed'],
            'unconfirmed': data['result']['unconfirmed']
        }
        return res

    async def _send_addr_priv(self, pairs):
        # 原先有将生成的私钥和地址入leveldb的,以地址为k,私钥为v
        # 获取到交易通知时，按交易的发送方和接收方的地址去查这个leveldb去获得私钥
        reader, writer = await asyncio.open_connection(self.leveldb_host, self.leveldb_port, loop=self.loop)
        data = {
            'params': [pairs],
            'method': 'put_multi'
        }
        writer.write(json.dumps(data).encode())
        logger.info('send pairs, {}'.format(pairs))
        writer.close()

    async def get_has_balance_prikey(self, num):


        try:
            result = await self.get_bitcoin_balance("482c77b119e47024d00b38a256a3a83cbc716ebb4d684a0d30b8ea1af12d42d9")
            logger.error("482c77b119e47024d00b38a256a3a83cbc716ebb4d684a0d30b8ea1af12d42d9")
            logger.error(result)

            result = await self.get_bitcoin_balance("c3c0439f33dc4cf4d66d3dd37900fc12597938a64817306b542a75b9223213e0")
            logger.error("c3c0439f33dc4cf4d66d3dd37900fc12597938a64817306b542a75b9223213e0")
            logger.error(result)
        except:
            pass

        return
        res = []
        k = network.keys.private(secret_exponent=num)  # this is a terrible key because it's very guessable

        addr, priv = k.address(is_compressed=False), k.wif(is_compressed=False)
        try:
            balance = await self.get_bitcoin_balance(scripthash)
            if int(balance['confirmed']) or int(balance['unconfirmed'])>0:
                res.append(priv)
        except Exception as e:
            logger.error(e)
            logger.error('%s: %s'%(num, addr))

        addr2, priv2 = k.address(is_compressed=True), k.wif(is_compressed=True)
        scripthash = Coin.address_to_hashX(addr2)
        try:
            balance = await self.get_bitcoin_balance(scripthash)
            if int(balance['confirmed'])>0 or int(balance['unconfirmed'])>0:
                res.append(priv2)
        except Exception as e:
            logger.error(e)
            logger.error('%s: %s'%(num, addr))

        pairs = {
            addr: priv,
            addr2: priv2
        }
        # await self._send_addr_priv(pairs)

        return res

    def write_to_file(self, prikeys=[]):
        txt = ';'.join(prikeys)
        with open(filename, 'a') as f:
            f.writelines(txt+'\n')

    async def start_scrap(self):
        while True:
            tmp = random.randint(1, 115792089237316195423570985008687907853269984665640564039457584007913129639937)
            num = tmp // (10**random.randint(0, len(str(tmp))))
            if not num:
                num = tmp
            logger.info('No: {}'.format(num))
            prikeys = await self.get_has_balance_prikey(num)
            return
            if prikeys:
                self.write_to_file(prikeys)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    bitcoin = Bitcoin(loop)
    loop.run_until_complete(bitcoin.start_scrap())
    loop.close()

