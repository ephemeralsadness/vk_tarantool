from copy import copy
from datetime import datetime
import random
import string
import tarantool


class TarantoolManager:
    def __init__(self, username, password):
        self.connection = tarantool.connect('localhost', 3301, user=username, password=password)

        self.links = {}
        self.reverse_links = {}
        self.amounts = {}
        self.last_times = {}

        # кортежи типа (link_id, link, amount, last_time)
        self.index = self.connection.space('index')

        # кортежи типа (ip, link_id)
        self.logs = self.connection.space('logs')

        self.ENCODE_SYMBOLS = string.ascii_letters + string.digits

    def encode(self, link):
        while True:
            short_link = ''.join(
                random.choice(self.ENCODE_SYMBOLS) for x in range(8)
            )

            if short_link not in self.links:
                return short_link

    def save_link(self, link):
        if link in self.reverse_links:
            return self.reverse_links[link]

        key = self.encode(link)
        self.links[key] = link
        self.reverse_links[link] = key
        self.amounts[key] = 0
        self.last_times[key] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return key

    def get_link(self, link_id):
        if link_id not in self.links:
            return None

        self.amounts[link_id] += 1
        self.last_times[link_id] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return self.links[link_id]

    def get_full_link(self, link_id):
        if link_id not in self.links:
            return None
        link = copy(self.links[link_id])
        amount = copy(self.amounts[link_id])
        last_time = copy(self.last_times[link_id])

        self.amounts[link_id] += 1
        self.last_times[link_id] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return link, amount, last_time
