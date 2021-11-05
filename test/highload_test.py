import random
import sys
import requests
from random import randrange
from urllib.parse import urljoin
from time import time


class HighloadTestManager:
    def __init__(self, address, websites_filename):
        self.address = address
        self.set_requests = 0
        self.get_requests = 0
        self.sites = []
        with open(websites_filename) as sites_file:
            self.sites = [line.strip() for line in sites_file.readlines()]
        self.short_links = []

    def set_link(self):
        site = random.choice(self.sites)
        resp = requests.post(urljoin(self.address, '/set'), data={'link': 'http://{}'.format(site)})
        self.short_links.append(resp.content)
        self.set_requests += 1

    def get_link(self):
        short_link = random.choice(self.short_links)
        requests.get(short_link)
        self.get_requests += 1



def main():
    address = sys.argv[1]
    websites_filename = sys.argv[2]
    spam_time = float(sys.argv[3])

    s = ['g' for _ in range(49)] + ['s']
    manager = HighloadTestManager(address, websites_filename)
    manager.set_link()

    start = time()
    while time() - start < spam_time:
        act = random.choice(s)
        if act == 's':
            manager.set_link()
        else:
            manager.get_link()

    print('Time in seconds: {}'.format(spam_time))
    print('Set requests: {}'.format(manager.set_requests))
    print('Get requests: {}'.format(manager.get_requests))


if __name__ == '__main__':
    main()
