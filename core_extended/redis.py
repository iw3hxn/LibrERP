# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

from walrus import *
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class Redis(object):
    def __init__(self, host, database, model):
        self.host = host
        self.model = model

        db_config = Database(host=host, db=0)
        config = db_config.Hash('config')

        db_index = config[database]
        if db_index:
            _logger.info("Find index {} for db {}".format(db_index, database))
        else:
            db_index = len(config.keys()) + 1

            while str(db_index) in config.values():
                db_index += 1

            config[database] = db_index
            _logger.info("Created new index {} for db {}".format(db_index, database))

        db_index = int(db_index)
        cache_db = Database(host=self.host, db=db_index)

        self.hash = cache_db.Hash(model)

    def __setitem__(self, key, item):
        self.hash[key] = item

    def __getitem__(self, key):
        value = self.hash[key]
        if value and value.isdigit():
            return int(value)
        elif value:
            try:
                value = float(value)
                return value
            except ValueError:
                return value
        else:
            return value

    def has_key(self, key):
        return key in self.hash

    def __contains__(self, item):
        return item in self.hash

    def expire(self):
        self.hash.expire(ttl=0)

    def empty(self):
        _logger.info("Deleting Redis cache...")
        self.expire()

    def __delitem__(self, key):
        del self.hash[key]

    def __len__(self):
        return len(self.hash)

    def keys(self):
        return self.hash.keys()


if __name__ == '__main__':
    # database = 'KST_123'
    database = 'KST_1'
    model = 'product.product'
    host = 'localhost'

    cache = Redis(host, database, model)

    cache[23] = "Rock'n'Roll"

    print(cache[23])

    cache.expire()
