#!/usr/bin/python

from atom import *
from data_processing import *
from math import cos, sin

class ZITTraderExo(Trader):
	def __init__(self, market, initial_assets=None, cash=0, sensitivity=0):
		Trader.__init__(self, market, initial_assets, cash)
		self.sensitivity = sensitivity
	def __str__(self):
		return "ZITExo %i" % self.trader_id
	def decide_order(self, market, asset):
		r = random.random() # 0 <= r < 1
		exo_info = market.orderbooks[asset].exo_info(market.time)
		price_inf = 1000 if exo_info <= 0 else min(9999, 1000+int(round(exo_info*self.sensitivity)))
		price_sup = 9999 if exo_info >= 0 else max(1000, 9999+int(round(exo_info*self.sensitivity)))
		return LimitOrder(asset, self, random.choice(['ASK', 'BID']), random.randint(price_inf, price_sup), random.randint(1, 9))

class MichaelMilken(Trader):
	'''Un charmant agent faisant des délits d'initié'''
	def __str__(self):
		return "Michael Milken"
	def decide_order(self, market, asset):
		r = random.random() # 0 <= r < 1
		info = np.mean([market.orderbooks[asset].exo_info(i) for i in range(market.time, market.time+5)])
		if info > .8 and market.orderbooks[asset].asks.size > 0:
			return LimitOrder(asset, self, 'BID', market.orderbooks[asset].asks.root().price, int(10*info))
		elif info < -.8 and market.orderbooks[asset].bids.size > 0:
			return LimitOrder(asset, self, 'ASK', market.orderbooks[asset].bids.root().price, int(-10*info))
		return None

file = open('trace.dat', 'w')
m = Market(['Google'], exo_infos=[(lambda x: sin(x/40))], out=file, trace=['price', 'wealth'], fix='L')
for i in range(2):
    m.add_trader(ZITTraderExo(m, initial_assets=[10], sensitivity=6000))
t = MichaelMilken(m, initial_assets=[10])
m.add_trader(t)
for i in range(1256):
    m.run_once()
file.close()

Wealths = extract_wealths('trace.dat')
T, W = Wealths['Michael Milken']
plt.plot(T, smooth(W, 10), '-', label="Michael Milken")
W_total = None
for agent in Wealths.keys():
	if "ZIT" in agent:
		T, W = Wealths[agent]
		W = np.array(W)
		W_total = W if type(W_total).__name__ == 'NoneType' else W_total + W
W = W_total/(len(Wealths)-1)
plt.plot(T, smooth(W, 10), '-', label="ZIT (mean)")
plt.grid()
plt.legend(loc='best')
plt.xlabel('Time')
plt.ylabel('Wealth')
plt.show()

print(t.get_infos(m))