#!/usr/bin/python

from atom import *

#out = open('trace.dat', 'w')
m = Market(['LVMH', 'Apple'], trace={i: False for i in ['tick', 'agent', 'price', 'wealth', 'orderbook']}, init_price=5500)
m.generate(2, 5, 10, 10000)
m.print_state()
#out.close()