import os

if __name__ == '__main__':
    for i in range(100):
        os.system('supervisorctl restart bitcoin_scraper:bitcoin_scraper-%02d' % i)

