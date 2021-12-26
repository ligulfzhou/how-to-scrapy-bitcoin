#!/usr/bin/env python3

"""
copy from https://github.com/bitcoin/bitcoin/blob/37a7fe9e440b83e2364d5498931253937abe9294/contrib/zmq/zmq_sub.py
"""
import binascii
import asyncio
import zmq
import zmq.asyncio
import signal
import struct
import sys

from tornado.options import options, define
define('debug', default=True, help='enable debug mode')
options.parse_command_line()

import pycoin.coins.Tx
from pycoin.coins.bitcoin.Tx import Tx
# from pycoin.tx.Tx import Tx
# from control import ctrl

port = 28332


class ZMQHandler():
    def __init__(self):
        self.loop = zmq.asyncio.install()
        self.zmqContext = zmq.asyncio.Context()

        self.zmqSubSocket = self.zmqContext.socket(zmq.SUB)
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "hashblock")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "hashtx")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "rawblock")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "rawtx")
        self.zmqSubSocket.connect("tcp://192.168.8.194:%i" % port)

    def rawtx(self, body):
        tx = Tx.from_bin(body)

        # orders = ctrl.api.get_orders_of_last_fifteen_minutes_ctl()
        # print(orders)
        # addr_order_dict = {i['bitaddr']: i for i in orders}
        # addrs = list(addr_order_dict.keys())

        for i in tx.txs_out:
            addr = i.address()

            # if addr not in addrs:
            #     continue
            #
            # order = addr_order_dict[addr]
            # if order['satoshi'] != i.coin_value:
            #     continue
            #
            # ctrl.api.update_order_ctl(order['order_id'], {
            #     'state': 1
            # })

    async def handle(self) :
        msg = await self.zmqSubSocket.recv_multipart()
        topic = msg[0]
        body = msg[1]
        sequence = "Unknown"
        if len(msg[-1]) == 4:
            msgSequence = struct.unpack('<I', msg[-1])[-1]
            sequence = str(msgSequence)

        if topic == b"hashblock":
            print('- HASH BLOCK ('+sequence+') -')
            print(binascii.hexlify(body))
        elif topic == b"hashtx":
            print('- HASH TX  ('+sequence+') -')
            print(binascii.hexlify(body))
        elif topic == b"rawblock":
            print('- RAW BLOCK HEADER ('+sequence+') -')
            print(binascii.hexlify(body[:80]))
        elif topic == b"rawtx":
            print('- RAW TX ('+sequence+') -')
            print(binascii.hexlify(body))

            self.rawtx(body)

        # schedule ourselves to receive the next message
        asyncio.ensure_future(self.handle())

    def start(self):
        self.loop.add_signal_handler(signal.SIGINT, self.stop)
        self.loop.create_task(self.handle())
        self.loop.run_forever()

    def stop(self):
        self.loop.stop()
        self.zmqContext.destroy()


daemon = ZMQHandler()
daemon.start()
