# -*- coding : utf-8 -*-

import random

liall = []
with open('hanzi', 'rb') as f:
    liall = reduce(lambda x, y: x + y, (line[5:-1].split(' ') for line in f))
    liall = [c.decode('utf8') for c in liall]
    print random.choice(liall)
