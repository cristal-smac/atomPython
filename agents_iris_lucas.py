import random
from atom_synchronous import *

class Trader(object):
    trader_count = 0
    def __init__(self, market, risk_aversion, aggressiveness, initial_assets=0, cash=0, loss_tolerance=None, expected_earnings=None):
        Trader.trader_count += 1
        self.trader_id = Trader.trader_count
        self.cash = cash
        self.assets = initial_assets
        self.risk_aversion = risk_aversion
        self.aggressiveness = aggressiveness
        self.herding = 'follower' if risk_aversion > 50 else 'contrarion'
        self.loss_tolerance = loss_tolerance
        self.expected_earnings = expected_earnings
    def __str__(self):
        return str(self.trader_id)
    def add_cash(self, n):
        self.cash += n
    def add_assets(self, n):
        self.assets += n

class MRA(Trader):
	''' Mean reversion agent'''
	def __init__(self, market, risk_aversion, aggressiveness, reversion_up, reversion_down, initial_assets=0, cash=0, loss_tolerance=None, expected_earnings=None):
		Trader.__init__(self, market, risk_aversion, aggressiveness, initial_assets, cash, loss_tolerance, expected_earnings)
		self.reversion_up = reversion_up
		self.reversion_down = reversion_down
	def __str__(self):
		return "MRA %i" % self.trader_id
	def decide_order(self, market):
		Delta = market.last_price - market.mean_price()
		delta = market.orderbook.tick_size()
		n = int(abs(self.aggressiveness/10 - 5))
		if (self.herding == 'follower' and Delta > self.reversion_up) or (self.herding == 'contrarion' and Delta < self.reversion_down):
			price = market.last_price + 10*n if delta == None else market.orderbook.asks.root().price + delta*n
			return LimitOrder(self, 'BID', price)
		elif (self.herding == 'contrarion' and Delta > self.reversion_up) or (self.herding == 'follower' and Delta < self.reversion_down):
			price = market.last_price - 10*n if delta == None else market.orderbook.bids.root().price - delta*n
			return LimitOrder(self, 'ASK', price)
		return None
	def update(self):
		delta = market.orderbook.tick_size()
		self.aggressiveness = random.randint(1,100)
		self.risk_aversion = random.randint(1,100)
		self.herding = 'follower' if self.risk_aversion > 50 else 'contrarion'
		self.reversion_up = delta//2
		self.reversion_down = -delta//2
	def still_valid(o):
		if o.direction == 'BID':
			return (self.herding == 'follower' and Delta > self.reversion_up) or (self.herding == 'contrarion' and Delta < self.reversion_down)
		else:
			return (self.herding == 'contrarion' and Delta > self.reversion_up) or (self.herding == 'follower' and Delta < self.reversion_down)