from atom import *
from numpy.random import normal, laplace, randint, uniform

# Comme la v0 mais avec une confiance en soi qui détermine les quantités envoyées

class Fundamentalist(Trader):
	def __init__(self, market, aggressiveness, self_confidence, initial_assets=None, cash=0):
		Trader.__init__(self, market, initial_assets, cash)
		self.alpha = aggressiveness
		self.gamma = self_confidence
		self.epsilon = random.randint(0,1) # Détermine si on achète ou en vend en cas d'égalité entre l'écart de m aux best orders
	def __str__(self):
		return "Fundamentalist %i" % self.trader_id
	def set_info(self, m, fv):
		self.wealth = self.get_wealth(m)
		self.fv = fv
	def decide_order(self, market, asset):
		m = self.fv
		p = market.prices[asset]
		best_ask = market.orderbooks[asset].asks.root().price if market.orderbooks[asset].asks.size > 0 else None
		best_bid = market.orderbooks[asset].bids.root().price if market.orderbooks[asset].bids.size > 0 else None
		if best_ask != None and best_ask < m:
			return LimitOrder('VAASM', self, 'BID', best_ask, self.gamma)
		elif best_bid != None and best_bid > m:
			return LimitOrder('VAASM', self, 'ASK', best_bid, self.gamma)
		else:
			best_ask = best_ask if best_ask != None else p
			best_bid = best_bid if best_bid != None else p
			if m-best_bid > best_ask-m or (m-best_bid == best_ask-m and self.epsilon == 1):
				p = int(round(best_bid + self.alpha*(m-best_bid)))
				return LimitOrder('VAASM', self, 'BID', p, 1)
			else:
				p = int(round(best_ask + self.alpha*(m-best_ask)))
				return LimitOrder('VAASM', self, 'ASK', p, 1)



opening_price = 1020
nb_days = 1
nb_ticks = 1000
nb_traders = 1000

file = open('trace.dat', 'w')
m = Market(['VAASM'], out=file, trace=['order', 'tick', 'price'], init_price=opening_price, fix='L')

# On créé nos agents
A = uniform(0, 1, nb_traders)
SC = randint(1, 10, nb_traders)
for i in range(nb_traders):
	m.add_trader(Fundamentalist(m, A[i], SC[i]))

# On fait tourner le marché...
fv = 1000
for d in range(nb_days):
	FV = normal(fv, fv*.05, nb_traders)
	for i, ag in enumerate(m.traders):
		ag.set_info(m, FV[i])
	for t in range(nb_ticks):
		m.run_once(shuffle=True)
	# for ag in m.traders:
	# 	if ag.get_wealth(m) > ag.wealth:
	# 		ag.gamma += 1
	# 	else:
	# 		ag.gamma = max(1, ag.gamma-1)
	fv += normal(0, 10)

m.out = sys.stdout
m.print_state()
file.close()