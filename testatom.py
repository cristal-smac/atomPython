#!/usr/bin/python

from atom import *

# out = open('trace.replay.dat', 'w')
# m = Market(out, print_orderbooks=False)
# m.add_asset(OrderBook('Apple'))
# m.add_asset(OrderBook('Microsoft'))

# m.replay('trace.dat')
# m.print_state()
# out.close()

# m = Market()
# m.add_asset(OrderBook('LVMH'))
# m.generate(['LVMH'], 2, 5)
# m.print_state()

out = open('BTCUSD.dat', 'w')
with open('Coinbase_BTCUSD_1h.csv', 'r') as file:
	i = 0
	for line in file:
		i += 1
		if i > 2:
			l = line.split(',')
			out.write("Price;BTCUSD;x;y;%i;qty;timestamp\n" % int(100*float(l[2])))
out.close()