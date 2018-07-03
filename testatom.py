#!/usr/bin/python

from atom import *
import random
from copy import copy
from math import log, sqrt, atan, tanh, pi

class AversionTrader(Trader):
	def __init__(self, market, risk_aversion, initial_assets=None, cash=0):
		Trader.__init__(self, market, initial_assets, cash)
		self.risk_av = risk_aversion
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
		r_low = log(self.lower)-log(pt)
		r_up = log(self.upper)-log(pt)
		r_mean = (r_low+r_up)/2
		r_var = (r_up-r_low)**2/12
		wa_opt = r_mean/(self.risk_av*r_var)
		wa_opt = tanh(r_mean/(risk_av*r_var))/2 +.5
		#wa_opt = 0.6*atan(r_mean/(risk_av*r_var))/pi +.5
		self.is_happy = abs((wa-wa_opt)/wa_opt) < .1
		qty = int(round((wa_opt*wealth)/pt - self.assets[asset]))
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
		if self.is_happy:
			return None
		price = random.randint(self.lower, self.upper)
		if self.last_sent_order != None:
			self.last_sent_order.cancel()
		if self.dir == 'ASK':
			self.qty = min(self.qty, self.assets[asset])
		if self.dir == 'BID':
			self.qty = min(self.qty, self.cash//market.prices[asset])
		if self.qty <= 0:
			return None
		self.last_sent_order = LimitOrder(asset, self, self.dir, price, self.qty)
		return self.last_sent_order


nb_days = 30
nb_ticks = 30
opening_price = 5100
fund_value = 5000

file = open('trace.dat', 'w')
m = Market(['Google'], out=file, trace=['order', 'tick', 'price'], init_price=opening_price)
m.print_last_prices()

for i in range(500):
	risk_av = random.randint(1, 10)
	init_cash = (2000000*(10-risk_av))//9
	init_invest = (2000000-init_cash)//opening_price
	ag = AversionTrader(m, risk_av, [init_invest], init_cash)
	ag.set_info(int(0.7*fund_value), int(1.3*fund_value))
	m.add_trader(ag)

for d in range(nb_days):
	t = int(time.time()*1000000-m.t0)
	m.write("LowerFundValue(New);%i;%i\nUpperFundValue(New);%i;%i\n" % (int(fund_value*0.7), t, int(fund_value*1.3), t))
	for ag in m.traders:
		ag.set_info(int(fund_value*0.7), int(fund_value*1.3))
	for t in range(nb_ticks):
	    m.run_once()
	t = int(time.time()*1000000-m.t0)
	m.write("LowerFundValue;%i;%i\nUpperFundValue;%i;%i\n" % (int(fund_value*0.7), t, int(fund_value*1.3), t))
	x = random.randint(500,1000)
	fund_value += x if fund_value <= 2000 else random.choice([-x, x])
	m.print_last_prices()

m.out = sys.stdout
m.print_state()
file.close()