from atom import *
from numpy.random import normal, laplace

class Fundamentalist(Trader):
	def __init__(self, market, aggressiveness, initial_assets=None, cash=0):
		Trader.__init__(self, market, initial_assets, cash)
		self.alpha = aggressiveness
		self.epsilon = random.randint(0,1) # Détermine si on achète ou en vend en cas d'égalité entre l'écart de m aux best orders
	def __str__(self):
		return "Fundamentalist %i" % self.trader_id
	def set_info(self, fv):
		self.fv = fv
	def decide_order(self, market, asset):
		m = self.fv
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
			if m-best_bid > best_ask-m or (m-best_bid == best_ask-m and self.epsilon == 1):
				p = int(round(best_bid + self.alpha*(m-best_bid)))
				return LimitOrder('VAASM', self, 'BID', p, 1)
			else:
				p = int(round(best_ask + self.alpha*(m-best_ask)))
				return LimitOrder('VAASM', self, 'ASK', p, 1)



opening_price = 1000
nb_ticks = 1000

file = open('trace.dat', 'w')
m = Market(['VAASM'], out=file, trace=['order', 'tick', 'price'], init_price=opening_price, fix='L')

# On créé nos agents
for p in [950, 1000, 1050]:
	for i in range(1,100):
		t = Fundamentalist(m, aggressiveness=i/100)
		t.set_info(p)
		m.add_trader(t)

# for i in range(1,10000):
# 	#p = normal(1000, 50)
# 	p = random.randint(900,1100)
# 	#p = laplace(1000,36)
# 	# if random.random() < .3:
# 	# 	p = 1000
# 	a = random.random()
# 	t = Fundamentalist(m, aggressiveness=a)
# 	t.set_info(p)
# 	m.add_trader(t)

# On fait tourner le marché...
for t in range(nb_ticks):
	m.run_once(shuffle=True)

m.out = sys.stdout
m.print_state()
file.close()