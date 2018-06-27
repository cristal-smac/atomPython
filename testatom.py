#!/usr/bin/python

from atom import *

class ZITTrader_v1bis(Trader):
    def __init__(self, market, initial_assets=None, cash=0, delta=0.05, pb_cancel=0.1):
        Trader.__init__(self, market, initial_assets, cash)
        self.delta = delta
        self.pb_cancel = pb_cancel
    def __str__(self):
        return "ZITbis %i" % self.trader_id
    def decide_order(self, market, asset):
        r = random.random() # 0 <= r < 1
        if r < self.pb_cancel:
            return CancelMyOrders(asset, self)
        else:
            last_price = market.prices[asset] if market.prices[asset] != None else 150
            price = random.randint(max(100, int((1-self.delta)*last_price)), max(int(100*(1+2*self.delta)), 1+int((1+self.delta)*last_price)))
            return LimitOrder(asset, self, random.choice(['ASK', 'BID']), price, random.randint(1, 9))


file = open('trace.dat', 'w')
m = Market(['Apple', 'Google'], out=file, trace=['price'], fix='S')
for i in range(10):
    m.add_trader(ZITTrader_v1bis(m, delta=0.05, pb_cancel=0.005))
for i in range(200000):
    m.run_once()
file.close()