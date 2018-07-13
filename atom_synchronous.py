#-----------------------------------------
#      ATOM Minimal Market Model
#
# Auteur  : Philippe MATHIEU
# Labo    : CRISTAL, Equipe SMAC
# Date    : 16/09/2010
# contact : philippe.mathieu@univ-lille.fr
#-----------------------------------------


#!/usr/bin/python
"""
   module atom
"""

import time
import random
import sys
import numpy as np


class LimitOrder(object):
    def __init__(self, source, direction, price):
        self.source = source
        self.price = price
        self.direction = direction.upper()
        self.time = None
    def __str__(self):
        return "LimitOrder;%s;%s;%i" % (self.source.__str__(), self.direction, self.price)
    def current_time(self, market):
        self.time = int(time.time()*1000000-market.t0)


class OrderBook:
    def __init__(self):
        # self.asks = bh.MinHeap(lambda x: (x.price, x.time))
        # self.bids = bh.MinHeap(lambda x: (-x.price, x.time))
        self.asks = []
        self.bids = []
        self.last_transaction = None
        self.tick_size = 10
    def add_order(self, order, market):
        market.nb_order_sent += 1
        if market.should_write('order'):
            market.write(order.__str__()+"\n")
        order.current_time(market)
        if order.direction == "BID":
            self.add_bid(order)
        else:
            self.add_ask(order)
    def tick_size_update(self):
        l = [o.price for o in self.asks+self.bids]
        if l == None:
            self.tick_size = 10
        else:
            l = list(set(l))
            if len(l) <= 1:
                self.tick_size = 10
            else:
                l = np.array(l)
                self.tick_size = min(l[1:]-l[:-1])
    def add_bid(self, order):
        self.bids.append(order)
        self.bids.sort(key = lambda x: (-x.price, x.time))
    def add_ask(self, order):
        self.asks.append(order)
        self.asks.sort(key = lambda x: (x.price, x.time))
    def imbalance(self):
        return abs(len(self.asks) - len(self.bids))
    def match(self, market):
        # Si une transaction est possible, l'effectue, sachant que le dernier ordre ajouté a pour direction dir. Sinon, retourne None.
        if (self.asks == []) or (self.bids == []):
            return None
        if self.asks[0].price > self.bids[0].price:
            return None
        ask = self.asks.pop(0)
        bid = self.bids.pop(0)
        price = bid.price if bid.time < ask.time else ask.price # Prend le prix de l'ordre le plus ancien
        # On modifie les agents
        ask.source.add_cash(price)
        ask.source.add_assets(-1)
        bid.source.add_cash(-price)
        bid.source.add_assets(1)
        self.last_transaction = (bid.source, ask.source, price)
        market.prices_last_tick.append(price)
        if market.should_write('trade'):
            market.write("Trade;%s;%s;%i;%i\n" % (bid.source.__str__(), ask.source.__str__(), price, market.time))
        market.nb_trades += 1
        return self.last_transaction


class Market:
    def __init__(self, out=sys.stdout, trace='all', init_price=5000, hist_len=100):
        # init_price : prix initial supposé des différents cours quand a aucun prix n'a encore été fixé (surtout utilisé pour le calcul du wealth)
        # hist_len : à un asset donné, nombre de prix gardés en mémoire par le marché
        self.t0 = time.time()*1000000
        self.time = 0
        self.traders = []
        self.orderbook = OrderBook()
        self.last_price = init_price
        self.best_ask = init_price
        self.best_bid = init_price
        self.prices_hist = []
        self.prices_last_tick = [init_price]
        self.out = out
        self.out_type = 'file' if type(out).__name__ == 'TextIOWrapper' or type(out).__name__ == 'OutStream' else 'None'
        self.nb_order_sent = 0
        self.nb_trades = 0
        self.hist_len = hist_len
        self.trace = {'always': self.out_type == 'file'}
        for info_type in ['order', 'tick', 'trade'] :
            self.trace[info_type] = trace == 'all' or (type(trace).__name__ == 'list' and info_type in trace) and self.out_type == 'file'
        # self.trace est un dictionnaire qui à un type d'information associe un booléen qui dit si on veut afficher cette info dans la trace
        self.write("# LimitOrder;asset;agent;direction;price;qty\n", i='order')
        self.write("# Tick;nb_tick;price;imbalance;nb_trades\n", i='tick')
        self.write("# Trade;bider;asker;price;tick\n", i='trade')
        # On créé un 'faux' historique des prix, sinon les agents seraient bloqués dès le premier tour...
        for i in range(hist_len-1):
            self.prices_hist.append(init_price+random.randint(-100, 100))
        self.prices_hist.append(init_price)
    def __str__(self):
        return "Market with %i traders" % len(self.traders)
    def should_write(self, info_type):
        return self.trace[info_type]
    def write(self, s, i='always'):
        if self.should_write(i):
            self.out.write(s)
    def mean_price(self):
        return int(sum(self.prices_hist)/len(self.prices_hist))
    def add_trader(self, trader):
        if not trader in self.traders:
            self.traders.append(trader)
    def remove_trader(self, trader):
        self.traders.remove(trader)
    def print_state(self):
        self.write("# Nb orders received: %i\n# Nb trades: %i\n# Leaving ask size: %i\n# Leaving bid size: %i\n" % (self.nb_order_sent, self.nb_trades, len(self.orderbook.asks), len(self.orderbook.bids)))
    def update_time(self):
        while self.orderbook.match(self) != None:
            pass
        self.time += 1
        if self.prices_last_tick != []:
            self.last_price = int(sum(self.prices_last_tick)/len(self.prices_last_tick))
        self.prices_hist.append(self.last_price)
        self.prices_last_tick = []
        if len(self.prices_hist) > self.hist_len:
            self.prices_hist.pop(0)
        if self.should_write('tick'):
            self.write("Tick;%i;%i;%i;%i\n" % (self.time, self.last_price, self.orderbook.imbalance(), self.nb_trades))
        self.best_ask = self.orderbook.asks[0].price if self.orderbook.asks != [] else self.last_price
        self.best_bid = self.orderbook.bids[0].price if self.orderbook.bids != [] else self.last_price
        self.orderbook.tick_size_update()
        # On met à jour des agents
        for t in self.traders:
            t.update(self)
        # Puis on demande à ces agents si ces ordres sont toujours valides
        for o in self.orderbook.asks:
            if not o.source.still_valid(self, o):
                self.orderbook.asks.remove(o)
        for o in self.orderbook.bids:
            if not o.source.still_valid(self, o):
                self.orderbook.bids.remove(o)
    def run_once(self):
        # Au sein d'un tour, chaque agent a exactement une fois la possibilité d'envoyer un ordre
        for t in self.traders:
            decision = t.decide_order(self)
            if decision != None:
                self.orderbook.add_order(decision, self)
        self.update_time()


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
        delta = market.orderbook.tick_size
        n = int(abs(self.aggressiveness/10 - 5))
        if (self.herding == 'follower' and Delta > self.reversion_up) or (self.herding == 'contrarion' and Delta < self.reversion_down):
            price = max(100, market.best_ask + delta*n)
            return LimitOrder(self, 'BID', price)
        elif (self.herding == 'contrarion' and Delta > self.reversion_up) or (self.herding == 'follower' and Delta < self.reversion_down):
            price = max(100, market.best_bid - delta*n)
            return LimitOrder(self, 'ASK', price)
        return None
    def update(self, market):
        self.aggressiveness = random.randint(1,100)
        self.risk_aversion = random.randint(1,100)
        self.herding = 'follower' if self.risk_aversion > 50 else 'contrarion'
        delta = market.orderbook.tick_size
        self.reversion_up = max(delta, 1)
        self.reversion_down = min(-delta, -1)
    def still_valid(self, market, o):
        Delta = market.last_price - market.mean_price()
        if o.direction == 'BID':
            return (self.herding == 'follower' and Delta > self.reversion_up) or (self.herding == 'contrarion' and Delta < self.reversion_down)
        else:
            return (self.herding == 'contrarion' and Delta > self.reversion_up) or (self.herding == 'follower' and Delta < self.reversion_down)



def extract_data(filename):
    Ticks = []
    Prices = []
    Imbalances = []
    Trades = []
    with open(filename, 'r') as file:
        for line in file:
            l = line.split(';')
            if l[0] == "Tick":
                Ticks.append(int(l[1]))
                Prices.append(int(l[2]))
                Imbalances.append(int(l[3]))
                Trades.append(int(l[4]))
    return Ticks, Prices, Imbalances, Trades