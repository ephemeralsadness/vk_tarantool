from copy import copy
from datetime import datetime
import random
import string
import tarantool
from recommender import Recommender
import socket
import struct


def ip2int(ip):
    return struct.unpack("!I", socket.inet_aton(ip))[0]


class TarantoolManager:
    def __init__(self, username, password):
        self.connection = tarantool.connect('localhost', 3301, user=username, password=password)

        # кортежи типа (link_id, link, amount, last_time)
        self.index = self.connection.space('index')

        # кортежи типа (ip, link_id)
        self.logs = self.connection.space('log')

        self.tuples = []
        self.recommender = Recommender([])

        self.ENCODE_SYMBOLS = string.ascii_letters + string.digits

    def encode(self, link):
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

        link_id = self.encode(link)
        self.index.insert((link_id, link, 0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return link_id

    def get_recommendations(self, ip):
        return self.recommender.recommend(ip2int(ip))

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

        self.tuples.append((ip2int(ip), link_id))
        if len(self.tuples) >= 1000:
            recommender = Recommender(self.tuples)
            self.tuples.clear()

        return found_link[0][1], found_link[0][2], found_link[0][3]
