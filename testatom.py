#!/usr/bin/python

from atom import *



# out = open('trace.replay.dat', 'w')
# m = Market(out, print_orderbooks=False)
# m.add_asset(OrderBook('Apple'))
# m.add_asset(OrderBook('Microsoft'))

# m.replay('trace.dat')
# m.print_state()
# out.close()



# out = open('trace.dat', 'w')
# m = Market(['LVMH', 'Apple'], out, print_orderbooks=True, init_price=5500)
# m.generate(2, 5, 10, 10000)
# m.print_state()
# out.close()

# print(extract_wealths('trace.dat'))



m = Market(['Apple'])
t = DumbAgent(m)
m.add_trader(t)
t.send_order(LimitOrder('Apple', t, 'ASK', 2567, 2), m)
