from atom import *

class Fundamentalist(Trader):
	def __init__(self, market, aggressiveness, initial_assets=None, cash=0):
		Trader.__init__(self, market, initial_assets, cash)
		self.alpha = aggressiveness
	def __str__(self):
		return "Fundamentalist %i" % self.trader_id
	def set_info(self, lower, upper):
		self.lower = lower
		self.upper = upper
	def decide_order(self, market, asset):
		u = self.upper
		l = self.lower
		m = (u+l)//2
		p = market.prices[asset]
		best_ask = market.orderbooks[asset].asks.root().price if market.orderbooks[asset].asks.size > 0 else None
		best_bid = market.orderbooks[asset].bids.root().price if market.orderbooks[asset].bids.size > 0 else None
		if best_ask != None and best_ask < m:
			return LimitOrder('VAASM', self, 'BID', best_ask, 1)
		elif best_bid != None and best_bid > m:
			return LimitOrder('VAASM', self, 'ASK', best_bid, 1)
		else:
			best_ask = best_ask if best_ask != None else p
			best_bid = best_bid if best_bid != None else p
			if m-best_bid >= best_ask-m:
				p = int(round(best_bid + self.alpha*(m-best_bid)))
				return LimitOrder('VAASM', self, 'BID', p, 1)
			else:
				p = int(round(best_ask + self.alpha*(m-best_ask)))
				return LimitOrder('VAASM', self, 'ASK', p, 1)



opening_price = 1020
nb_ticks = 10

file = open('trace.dat', 'w')
m = Market(['VAASM'], out=file, trace=['order', 'tick', 'price'], init_price=opening_price, fix='L')

# On créé nos agents
for p in [950, 1000, 1050]:
	for i in range(1,100):
		t = Fundamentalist(m, aggressiveness=i/100)
		t.set_info(p-100, p+100)
		m.add_trader(t)

# On fait tourner le marché...
for t in range(nb_ticks):
	m.run_once(shuffle=True)

m.out = sys.stdout
m.print_state()
file.close()


w = [0, 0, 0]
for t in m.traders:
	w[(t.trader_id-1)//99] += t.get_wealth(m)
print("Wealth (fv=950): %.2f\nWealth (fv=1000): %.2f\nWealth (fv=1050): %.2f\n" % (w[0]/99, w[1]/99, w[2]/99))

from data_processing import *

Prices = extract_prices('trace.dat')
T, P = Prices['VAASM']
plt.plot(T, P, '-')
plt.xlabel("Time")
plt.ylabel("Price")
plt.show()