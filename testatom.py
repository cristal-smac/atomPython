#!/usr/bin/python

from atom import *

# out = open('trace.replay.dat', 'w')
# m = Market(out, print_orderbooks=False)
# m.add_asset(OrderBook('Apple'))
# m.add_asset(OrderBook('Microsoft'))

# m.replay('trace.dat')
# m.print_state()
# out.close()

m = Market()
m.add_asset(OrderBook('LVMH'))
m.generate(['LVMH'], 2, 5)
m.print_state()