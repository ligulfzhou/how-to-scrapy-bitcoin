import json
import socket
from pycoin.key.Key import Key
from flask import Flask, render_template, jsonify

PAGE_SIZE = 64
app = Flask(__name__)


ELECTRUMX_HOST = '69.51.11.34'
ELECTRUMX_PORT = 50001

class Bitcoin:

    def __init__(self):
        pass
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.connect(('69.51.11.34', 50001))

    def get_key_pair(self, intx, use_uncompressed=False):
        k = Key(intx)
        res = {
            'int': intx,
            'address': k.address(use_uncompressed=use_uncompressed),
            'private_key': k.wif(use_uncompressed=use_uncompressed)
        }
        return res

    def get_key_pairs(self, intx):
        k = Key(intx)
        res = {
            'num': intx,
            'address': k.address(use_uncompressed=False),
            'private_key': k.wif(use_uncompressed=False),
            'compressed_address': k.address(use_uncompressed=True),
            'compressed_private_key': k.wif(use_uncompressed=True)
        }
        return res

    def get_address_balance(self, address):
        params = {
            'jsonrpc': '2.0',
            'method': 'blockchain.address.get_balance',
            'params': [address],
            'id': address
        }
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('69.51.11.34', 50001))
        self.socket.sendall(json.dumps(params).encode() + b'\n')
        data = self.socket.recv(4096)
        logging.error(json.loads(data))
        data = json.loads(data)
        res = {
            'address': address,
            'confirmed': data['result']['confirmed'],
            'unconfirmed': data['result']['unconfirmed']
        }
        return res

    def get_addresses_balance(self, addresses):
        params = [{
            'jsonrpc': '2.0',
            'method': 'blockchain.address.get_balance',
            'params': [address],
            'id': address
        } for address in addresses]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('69.51.11.34', 50001))
        self.socket.sendall(json.dumps(params).encode() + b'\n')
        data = self.socket.recv(4096)
        logging.error(json.loads(data))
        data = json.loads(data)
        res = {
            d['id']: {
                'confirmed': d['result']['confirmed'],
                'unconfirmed': d['result']['unconfirmed']
            }
            for d in data
        }
        return res


bitcoin = Bitcoin()


@app.context_processor
def utility_processor():
    def json_format(data):
        if isinstance(data, str):
            return data
        return json.dumps(data)
    return dict(json_format=json_format)


@app.route('/<int:page>')
def bitcoin_pairs_at_page(page):
    start, end = (page - 1) * PAGE_SIZE + 1, page * PAGE_SIZE
    key_pairs = []
    ths = ['num', 'private_key', 'address', 'compressed_private_key', 'compressed_address']

    [key_pairs.append(bitcoin.get_key_pairs(i)) for i in range(start, end + 1)]
    start, step, times = 0, 10, 7
    addr_balances = {}
    for i in range(times):
        addrs = []
        for k in key_pairs[start*i: start*i + step]:
            addrs.extend([k['address'], k['compressed_address']])
        addr_values = bitcoin.get_addresses_balance(addrs)
        addr_balances.update(addr_values)

    return render_template('bitcoin_key_pairs.html', key_pairs=key_pairs, page=page,
                           from_hex=start, to_hex=end, ths=ths, addr_balances=addr_balances)


@app.route('/address/balance')
def get_address_balance():
    try:
        address = request.args['address']
        address = address.split(',')
        address = list(map(str.strip, address))
    except:
        return jsonify(dict(errcode=10001, errmsg='参数错误'))

if __name__ == '__main__':
    app.run(debug=True)
