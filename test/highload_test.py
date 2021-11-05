import requests
from random import randrange

with open('companies.txt') as companies:
    for line in companies:
        line = line.rstrip()
        ip = '{}.{}.{}.{}'.format(randrange(256), randrange(256), randrange(256), randrange(256))
        requests.post('{}'.format('http://87.239.110.13'), data={'link': })
