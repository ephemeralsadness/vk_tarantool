from datetime import datetime
import random
import string
import tarantool
from recommender import Recommender
import socket
import struct
from collections import defaultdict


def ip2int(ip):
    return struct.unpack("!I", socket.inet_aton(ip))[0]


class TarantoolManager:
    def __init__(self, username, password):
        self.connection = tarantool.connect('localhost', 3301, user=username, password=password)

        # кортежи типа (link_id, link, amount, last_time)
        self.index = self.connection.space('index')

        self.tuples = defaultdict(int)
        self.recommender = Recommender([('127.0.0.1', 'https://vk.com', 1)])

        self.ENCODE_SYMBOLS = string.ascii_letters + string.digits

    def encode(self):
        while True:
            short_link = ''.join(
                random.choice(self.ENCODE_SYMBOLS) for x in range(8)
            )

            tuples = self.index.select(short_link)
            if len(tuples) == 0:
                return short_link

    def save_link(self, link):
        found_link = self.index.select(link, index=1)
        if len(found_link) != 0:
            return found_link[0][0]

        link_id = self.encode()
        self.index.insert((link_id, link, 0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return link_id

    def get_recommendations(self, ip):
        a = self.recommender.recommend(ip2int(ip))
        print(a)
        return a

    def get_link(self, link_id, ip):
        return self.get_full_link(link_id, ip)[0]

    def get_full_link(self, link_id, ip):
        found_link = self.index.select(link_id)
        if len(found_link) == 0:
            return None

        self.index.update(link_id, [
            ('+', 2, 1),
            ('=', 3, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ])

        self.tuples[(ip2int(ip), link_id)] += 1
        n = len(self.tuples)
        if n > 0 and n & (n - 1) == 0:
            a = [(key[0], key[1], value) for key, value in self.tuples.items()]
            self.recommender = Recommender(a)
            self.tuples = defaultdict(int)

        return found_link[0][1], found_link[0][2], found_link[0][3]
