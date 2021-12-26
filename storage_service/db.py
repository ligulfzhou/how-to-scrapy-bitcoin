import plyvel


class DB(object):

    def __init__(self):
        self.addr_privkey = plyvel.DB('/Users/ligangzhou/.electrumx/addr_privkey', create_if_missing=True, max_open_files=128)
        self.mnemonic_path = plyvel.DB('/Users/ligangzhou/.electrumx/mnemonic_path', create_if_missing=True, max_open_files=128)

    def get_privkey_of_addr(self, addr: str) -> str:
        privkey = self.addr_privkey.get(addr.encode())
        if privkey:
            privkey = privkey.decode()
        return privkey

    def save_kp(self, kp: dict) -> None:
        '''kp: {address, privkey}'''
        self.addr_privkey.put(kp['address'].encode(), kp['privkey'].encode())

    def save_mnemonic_path(self, kp: dict) -> None:
        '''kp: {mnemonic, path}'''
        self.mnemonic_path.put(kp['mnemonic'].encode(), kp['path'].encode())

    def get_path_of_mnemonic(self, mnemonic: str) -> str:
        path = self.mnemonic_path.get(mnemonic.encode())
        if path:
            path = path.decode()
        return path

    def get_iterator(self, db: int, **kw):
        if db == 0:
            return self.addr_privkey.iterator(**kw)
        return self.mnemonic_path.iterator(**kw)

    def delete_addr(self, keys: [str]):
        for key in keys:
            self.addr_privkey.delete(key.encode())

    def delete_mnemonic(self, keys: [str]):
        for key in keys:
            self.mnemonic_path.delete(key.encode())

if __name__ == '__main__':
    db = DB()
    # for i in range(1000):
    #     db.delete_addr([f'test'])
    #     db.delete_mnemonic([f'test'])
    #     db.save_kp({
    #         'address': f'test{i}',
    #         'privkey': f'privkey{i}'
    #     })
    #     db.save_mnemonic_path({
    #         'mnemonic': f'test{i}',
    #         'path': f'privkey{i}'
    #     })
    print('='*10)
    for k, v in db.get_iterator(0):
        print(f'k: {k}\t v: {v}')

    print('='*10)
    for k, v in db.get_iterator(1):
        print(f'k: {k}\t v: {v}')
