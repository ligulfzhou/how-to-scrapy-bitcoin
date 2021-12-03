import sys
import asyncio
import logging
import binascii
import time
import requests
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from aiorpcx import timeout_after, connect_rs
from pycoin.symbols.btc import network
from bip32utils import BIP32Key, BIP32_HARDEN
from mnemonic import Mnemonic

logger = logging.getLogger("random_mnemonic_codes")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler = RotatingFileHandler("random_mnemonic_codes.log", maxBytes=104857600, backupCount=1)
handler.setFormatter(formatter)
logger.addHandler(handler)

stderr = StreamHandler(sys.stderr)
stderr.setFormatter(formatter)
logger.addHandler(stderr)

indexname = 'mnemonic_index'
filename = 'mnemonic.txt'
valid_with_transaction = 'valid_mnemonic.txt'

derivation_paths = ["m/0'/0'", "m/0'/0", "m/44'/0'/0'", "m/44'/0'/0'/0", "m/49'/0'/0'/0", "m/84'/0'/0'/0", "m/0"]


class MnemonicCode:

    def __init__(self, loop):
        self.loop = loop
        self.electrumx_host = 'localhost'
        self.electrumx_port = 8000
        self.storage_url = 'http://localhost:8080/save'

    def get_script(self, addr):
        return binascii.hexlify(network.parse.address(addr).script()).decode()

    async def get_bitcoin_balance(self, address, mnemonic_code, path) -> (bool, bool):
        async with timeout_after(30):
            async with connect_rs(self.electrumx_host, self.electrumx_port) as session:
                have_balance, have_transaction = False, False
                script = self.get_script(address)
                session.transport._framer.max_size = 0
                result = await session.send_request('query', {'items': [script], 'limit': 1})
                logger.info("address: %s, result: %s" % (address, result))
                if float(result[-1].strip('Balance:').strip('BTC')):
                    self.write_to_file([mnemonic_code])
                    have_balance = True

                if result[1] != 'No history found':
                    have_transaction = True
                    print(f'save mnemonic: {mnemonic_code} to storage service.....')
                    requests.post(self.storage_url, json={
                        'mnemonic': mnemonic_code,
                        'path': path
                    })
                return have_balance, have_transaction

    def write_to_file(self, prikeys=[]):
        txt = ';'.join(prikeys)
        with open(filename, 'a') as f:
            f.writelines(txt + '\n')

    def _get_random_words(self) -> [str]:
        m = Mnemonic('english')
        return m.generate().split(' ')

    def _get_bip_path(self, words, derivation_path):
        a = Mnemonic('english')
        words = ' '.join(words)
        entropy = a.to_seed(words)
        c = BIP32Key.fromEntropy(entropy)

        show_harden, begin_3, begin_bc = 0, 0, 0
        p = c.ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN)

        if derivation_path == "m/0'/0'":
            # bitcoin core:  m/0'/0'
            show_harden = 1
        elif derivation_path == "m/0'/0":
            # Multibit Use path m/0'/0.
            p = c.ChildKey(0 + BIP32_HARDEN).ChildKey(0)
        elif derivation_path == "m/44'/0'/0'":
            # blockchain.info m/44'/0'/0'
            p = c.ChildKey(44 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN)
        elif derivation_path == "m/44'/0'/0'/0":
            # bip44
            p = c.ChildKey(44 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0)
        elif derivation_path == "m/49'/0'/0'/0":
            # bip 49
            p = c.ChildKey(49 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0)
            begin_3 = 1
        elif derivation_path == "m/84'/0'/0'/0":
            # bip 84
            p = c.ChildKey(84 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0)
            begin_bc = 1
        elif derivation_path == "m/0":
            p = c.ChildKey(0)
            begin_3 = 1

        return p, show_harden, begin_bc, begin_3

    def _get_key_pair(self, i, p, show_harden, begin_bc, begin_3):
        if show_harden:
            cur = p.ChildKey(i + BIP32_HARDEN)
        else:
            cur = p.ChildKey(i)

        if begin_bc or begin_3:
            address = cur.P2WPKHoP2SHAddress()
        else:
            address = cur.Address()
        return {
            'address': address,
            'privkey': cur.WalletImportFormat()
        }

    async def check_words_at_random(self) -> None:
        words = self._get_random_words()

        for derivation_path in derivation_paths:
            p, show_harden, begin_bc, begin_3 = self._get_bip_path(words, derivation_path)
            idx = 0
            while True:
                kp = self._get_key_pair(idx, p, show_harden, begin_bc, begin_3)
                have_balance, have_transaction = False, False
                print(f'get kp: {kp} from mnemonic: {" ".join(words)} with derivation_path: {derivation_path} and index: {idx}')
                while True:
                    try:
                        have_balance, have_transaction = await self.get_bitcoin_balance(kp['address'], ' '.join(words), derivation_path)
                        break
                    except Exception as e:
                        print(e)
                        time.sleep(5)
                if not have_balance and not have_transaction:
                    break

                idx += 1

    async def start_scrap(self):
        while True:
            await self.check_words_at_random()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    mnemonic_code = MnemonicCode(loop)
    loop.run_until_complete(mnemonic_code.start_scrap())
    loop.close()
