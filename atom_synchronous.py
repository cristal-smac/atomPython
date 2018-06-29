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
import binary_heap as bh
from agents_iris_lucas import *


class LimitOrder(object):
    def __init__(self, source, direction, price):
        self.source = source
        self.price = price
        self.direction = direction.upper()
        self.time = None
        self.canceled = False
    def __str__(self):
        return "LimitOrder;%s;%s;%i" % (self.source.__str__(), self.direction, self.price)
    def cancel(self):
        self.canceled = True
    def current_time(self, market):
        self.time = int(time.time()*1000000-market.t0)


class OrderBook:
    def __init__(self):
        self.asks = bh.MinHeap(lambda x: (x.price, x.time))
        self.bids = bh.MinHeap(lambda x: (-x.price, x.time))
        self.last_transaction = None
    def add_order(self, order, market):
        market.nb_order_sent += 1
        if market.should_write('order'):
            market.write(order.__str__()+"\n")
        order.current_time(market)
        if order.direction == "BID":
            self.add_bid(order)
        else:
            self.add_ask(order)
    def add_bid(self, order):
        self.bids.insert(order)
    def add_ask(self, order):
        self.asks.insert(order)
    def imbalance(self):
        return abs(self.asks.size - self.bids.size)
    def match(self, market):
        # Si une transaction est possible, l'effectue, sachant que le dernier ordre ajouté a pour direction dir. Sinon, retourne None.
        while self.asks.size > 0 and self.asks.root().canceled:
            self.asks.extract_root()
        while self.bids.size > 0 and self.bids.root().canceled:
            self.bids.extract_root()
        if (self.asks.size == 0) or (self.bids.size == 0):
            return None
        if self.asks.root().price > self.bids.root().price:
            return None
        ask = self.asks.extract_root()
        bid = self.bids.extract_root()
        price = bid.price if bid.time < ask.time else ask.price # Prend le prix de l'ordre le plus ancien
        # On modifie les agents
        ask.source.add_cash(price)
        ask.source.add_assets(self.name, -1)
        bid.source.add_cash(-price)
        bid.source.add_assets(self.name, 1)
        self.last_transaction = (bid.source, ask.source, price)
        market.last_price = price
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
    def add_trader(self, trader):
        if not trader in self.traders:
            self.traders.append(trader)
    def remove_trader(self, trader):
        self.traders.remove(trader)
    def print_state(self):
        self.write("# Nb orders received: %i\n# Nb trades: %i\n# Leaving ask size: %i\n# Leaving bid size: %i\n" % (self.nb_order_sent, self.nb_trades, self.orderbook.asks.size, self.orderbook.bids.size))
    def update_time(self):
        while self.orderbook.match(self) != None:
            pass
        self.time += 1
        self.last_price = int(sum(self.prices_last_tick)/len(self.prices_last_tick))
        self.prices_hist.append(self.last_price)
        if len(self.prices_hist) > self.hist_len:
            self.prices_hist.pop(0)
        if self.should_write('tick'):
            self.write("Tick;%i;%i;%i;%i\n" % (self.time, self.last_price, self.orderbook.imbalance(), self.nb_trades))
        # On met à jour des agents
        for t in self.traders:
            t.update()
        # Puis on demande à ces agents si ces ordres sont toujours valides
        for o in self.orderbook.asks.tree+self.orderbook.bids.tree:
            if not o.source.still_valid(o):
                o.canceled = True
    def run_once(self):
        # Au sein d'un tour, chaque agent a exactement une fois la possibilité d'envoyer un ordre
        for t in self.traders:
            decision = t.decide_order(self)
            if decision != None:
                self.orderbook.add_order(decision, self)
        self.update_time()


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
    return Tick, Prices, Imbalances, Trades