#!/usr/bin/python

from atom import *
import random
from copy import copy
from math import log, sqrt, atan, tanh, pi, sin
from numpy.random import normal, triangular


nb_days = 1
nb_ticks = 5000
opening_price = 5500
fund_value = 5000
hist_len=100


class AversionTrader(Trader):
	def __init__(self, market, risk_aversion, aggressiveness, follower, initial_assets=None, cash=0):
		Trader.__init__(self, market, initial_assets, cash)
		self.risk_av = risk_aversion
		self.aggressiveness = aggressiveness
		self.follower = follower
		self.last_sent_order = None
	def __str__(self):
		return "AversionTrader %i" % self.trader_id
	def set_info(self, lower, upper):
		self.lower = lower
		self.upper = upper
	def compute_state(self, market, asset):
		pt = market.prices[asset]
		invest_value = self.assets[asset]*pt
		wealth = invest_value + self.cash
		wa = invest_value/wealth
		u = self.upper ; l = self.lower
		r_mean = ((u+l)/2-pt)/pt
		r_var = (u-l)**2/(12*pt**2)
		wa_opt = r_mean/(self.risk_av*r_var)
		# wa_opt = tanh(r_mean/(risk_av*r_var))/2 +.5
		# wa_opt = atan(r_mean/(risk_av*r_var))/pi +.5
		# On calcule la quantité
		qty = int(round((wa_opt*wealth)/pt - self.assets[asset]))
		# On calcule prix et direction
		# self.price = random.randint(l, u)
		if qty < 0:
			self.dir = 'ASK'
			self.qty = -qty
		else:
			self.dir = 'BID'
			self.qty = qty
	def notify(self, o1, o2):
		self.last_sent_order = o2
	def decide_order(self, market, asset):
		if random.random() < .9:
			return None
		self.compute_state(market, asset)
		if self.last_sent_order != None:
			self.last_sent_order.cancel()
		self.price = random.randint(self.lower, self.upper)
		#price = triangular(self.lower, (self.lower+self.upper)/2, self.upper)
		#
		# Prix déterministe :
		#
		# # Tentative 1
		#
		# 1 - On vire les ordres annulés de l'orderbook
		# while market.orderbooks[asset].asks.size > 0 and market.orderbooks[asset].asks.root().canceled:
		# 	market.orderbooks[asset].asks.extract_root()
		# while market.orderbooks[asset].bids.size > 0 and market.orderbooks[asset].bids.root().canceled:
		# 	market.orderbooks[asset].bids.extract_root()
		# # 2 - On récupère le prix du best bid et du best ask
		# best_ask = market.orderbooks[asset].asks.root().price if market.orderbooks[asset].asks.root() != None else market.prices[asset]
		# best_bid = market.orderbooks[asset].bids.root().price if market.orderbooks[asset].bids.root() != None else market.prices[asset]
		# # 3 - On calcule l'espérance de la valeur fondamentale
		# fv = (self.lower + self.upper)//2
		# # 4 - On calcule le best ask/bid "ajusté à la fv"
		# bat = (4*best_ask + fv)/5
		# bbt = (4*best_bid + fv)/5
		# # 5 - On calcule le coefficient d'instabilité du marché puis finalement, on calcule le prix
		# instability = (8*(best_ask-best_bid)/fv + abs(best_ask-fv)/fv + abs(best_bid+fv)/fv)/10
		# if self.dir == 'ASK':
		# 	price = int(bat-3*instability*(self.upper-self.lower)*self.aggressiveness/30)
		# if self.dir == 'BID':
		# 	price = int(bbt+3*instability*(self.upper-self.lower)*self.aggressiveness/30)
		#
		# Tentative 2
		#
		# u = self.upper
		# l = self.lower
		# if self.dir == 'BID':
		# 	price = l + (self.aggressiveness*(u-l))//10
		# elif self.dir == 'ASK':
		# 	price = u - (self.aggressiveness*(u-l))//10
		#
		# Tentative 3
		#
		# On vérifie que l'agent n'a ni cash ni asset négatif
		if self.dir == 'ASK':
			self.qty = min(self.qty, self.assets[asset])
		if self.dir == 'BID':
			self.qty = min(self.qty, self.cash//market.prices[asset])
		if self.qty <= 0:
			return None
		self.last_sent_order = LimitOrder(asset, self, self.dir, self.price, self.qty)
		return self.last_sent_order


file = open('trace.dat', 'w')
m = Market(['Google'], out=file, trace=['order', 'tick', 'price'], init_price=opening_price, fix='L', hist_len=hist_len)
for i in range(hist_len-1):
	m.prices_hist['Google'].append(opening_price)
m.print_last_prices()

for i in range(500):
	risk_av = random.randint(1, 10)
	agrness = random.randint(0, 10)
	init_cash = (2000000*(10-risk_av))//10
	init_invest = (2000000-init_cash)//opening_price
	# init_cash = 1000000
	# init_invest = 1000000//opening_price
	ag = AversionTrader(m, risk_av, agrness, random.choice([True, False]), [init_invest], init_cash)
	m.add_trader(ag)
for i in range(500):
	m.add_trader(ZITTrader(m, initial_assets=[1000000//opening_price], cash=1000000))

for d in range(nb_days):
	# x_up = 1.1 + random.random()*.15
	# x_low = 0.9 - random.random()*.15
	lower = int(0.7*fund_value)
	upper = int(1.3*fund_value)
	t = int(time.time()*10**9-m.t0)
	m.write("Day;%i;%i;%i\n" % (d, t, m.time+1))
	m.write("LowerFundValue;%i;%i\nFundValue;%i;%i\nUpperFundValue;%i;%i\n" % (lower, t, fund_value, t, upper, t))
	for ag in m.traders:
		ag.set_info(lower, upper)
	for t in range(nb_ticks):
	    m.run_once()
	t = int(time.time()*10**9-m.t0)
	m.write("LowerFundValue;%i;%i\nFundValue;%i;%i\nUpperFundValue;%i;%i\n" % (lower, t, fund_value, t, upper, t))
	# On rajoute des dividendes
	# for ag in m.traders:
	# 	ag.add_cash(.01*ag.assets['Google']*fund_value)
	# On met à jour la fund value
	x = random.random()*.05+.95
	x = random.choice([x, 1/x])
	fund_value = int(fund_value*x)
	m.print_last_prices()

m.out = sys.stdout
m.print_state()
file.close()