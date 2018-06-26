#!/usr/bin/python

from atom import *

out = open('trace.dat', 'w')
m = Market(['LVMH', 'Apple'], out, print_orderbooks=True, init_price=5500)
m.generate(2, 5, 10, 10000)
m.print_state()
out.close()

print(extract_prices('trace.dat'))