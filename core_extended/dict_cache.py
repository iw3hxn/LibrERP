# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)


class SimpleCache(dict):
    """
    This class works like a standard dict, but adds possibility to empty dict
    by calling empty() method instead of assigning new empty dict.
    Class is used to have the same interface between dict and Redis based cache
    """
    def empty(self):
        self.clear()

    def clear(self):
        return super(SimpleCache, self).clear()


if __name__ == '__main__':

    d = SimpleCache()

    d[1] = 'Product'
    d[2] = 'Airplane'

    print(d[2])

    d.empty()

    print(d)

    d[2] = 'Pears'
    print(d[2])
