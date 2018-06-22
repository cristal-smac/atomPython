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

import random
import sys
import pylab as plt
import numpy as np
import pandas as pd

import binary_heap as bh
from data_processing import *


class Order:
    def __init__(self, asset, source):
        self.asset = asset
        self.source = source

class LimitOrder(Order):
    def __init__(self, asset, source, direction, price, qty):
        Order.__init__(self, asset, source)
        self.price = price
        self.direction = direction.upper()
        self.qty = qty
        self.canceled = False
    def __str__(self):
        return "LimitOrder;%s;%s;%s;%i;%i" % (self.asset, self.source.__str__(), self.direction, self.price, self.qty)
    def decrease_qty(self, q):
        self.qty -= q
    def attribute_list(self):
        return [self.asset, self.source.__str__(), self.direction, self.price, self.qty]
    def cancel(self):
        self.canceled = True

class CancelOrder(Order):
    def __str__(self):
        return "CancelOrder;%s;%s" % (self.asset, self.source.__str__())


class Trader(object):
    trader_count = 0
    def __init__(self, available_assets=[], initial_assets=None, cash=0):
        Trader.trader_count += 1
        self.trader_id = Trader.trader_count
        self.cash = cash
        self.available_assets = available_assets
        self.assets = dict()
        if initial_assets == None:
            initial_assets = [0]*len(available_assets)
        for asset in available_assets:
            self.assets[asset] = initial_assets[available_assets.index(asset)]
    def __str__(self):
        return str(self.trader_id)
    def make_available(self, asset, qty=0):
        available_assets.append(asset)
        self.assets[asset] = qty
    def remove(self, asset):
        available_assets.remove(asset)
        self.assets.pop(asset)
    def place_order(self, market):
        raise NotImplementedException
    def add_cash(self, n):
        self.cash += n
    def add_assets(self, asset, n):
        self.assets[asset] += n
    def get_wealth(self, market, init_price=0):
        '''init_price: valeur supposée d'un asset quand aucun prix n'a encore été fixé '''
        w = self.cash
        for asset in self.available_assets:
            w += self.assets[asset]*(market.prices[asset] if market.prices[asset] != None else init_price)
        return w
    def get_infos(self, market):
        s = self.__str__()+":\nCash: "+str(self.cash)+"\n"
        for asset in self.available_assets:
            s += asset+": "+str(self.assets[asset])+"\n"
        s += "Wealth: "+str(self.get_wealth(market))+"\n"
        return s


class ZITTrader(Trader):
    def __str__(self):
        return "ZIT " + super().__str__()
    def place_order(self, market):
        return LimitOrder(random.choice(self.available_assets), self, random.choice(['ASK', 'BID']), random.randint(1000, 9999), random.randint(1, 9))


class OrderBook:
    def __init__(self, name):
        self.name = name
        self.bids = bh.MaxHeap(lambda x: x.price)
        self.asks = bh.MinHeap(lambda x: x.price)
        self.last_transaction = None
    def __str__(self):
        Asks = "" ; Bids = ""
        l_a = self.asks.tree[:] ; l_a.sort(key=(lambda x: x.price))
        l_b = self.bids.tree[:] ; l_b.sort(key=(lambda x: -x.price))
        for order in l_a:
            Asks += "\t"+order.__str__()+"\n"
        for order in l_b:
            Bids += "\t"+order.__str__()+"\n"
        return "\nOrderBook "+self.name+":\nAsks:\n"+(Asks if Asks != "" else "\tEmpty\n")+"Bids:\n"+(Bids if Bids != "" else "\tEmpty\n")+"\n"
    def add_order(self, order, market):
        market.nb_order_sent += 1
        if type(order).__name__ == 'LimitOrder':
            if order.direction == "BID":
                self.add_bid(order)
            else:
                self.add_ask(order)
            while self.match(order.direction, market) != None:
                pass
        elif type(order).__name__ == 'CancelOrder':
            for o in self.asks.tree:
                if o.source == order.source:
                    o.cancel()
            for o in self.bids.tree:
                if o.source == order.source:
                    o.cancel()
        market.out.write(order.__str__()+"\n")
    def add_bid(self, order):
        self.bids.insert(order)
    def add_ask(self, order):
        self.asks.insert(order)
    def has_order_from(self, source):
        return source in [o.source for o in self.bids.tree]+[o.source for o in self.asks.tree]
    def match(self, dir, market): # Si une transaction est possible, l'effectue, sachant que le dernier ordre ajouté a pour direction dir. Sinon, retourne None.
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
        qty = min(ask.qty, bid.qty)
        price = bid.price if dir == 'ASK' else ask.price # Prend le prix de l'ordre le plus ancien
        if ask.qty > qty:
            ask.decrease_qty(qty)
            self.asks.insert(ask)
        if bid.qty > qty:
            bid.decrease_qty(qty)
            self.bids.insert(bid)
        # On modifie les agents
        ask.source.add_cash(price*qty)
        ask.source.add_assets(self.name, -qty)
        bid.source.add_cash(-price*qty)
        bid.source.add_assets(self.name, qty)
        self.last_transaction = (bid.source, ask.source, price, qty)
        market.prices[self.name] = price
        # On affiche le prix
        market.out.write("Price;%s;%s;%s;%i;%i\n" % (self.name, bid.source.__str__(), ask.source.__str__(), price, qty))
        market.nb_fixed_price += 1
        # On affiche les agents qui ont été modifiés
        if market.print_agent:
            market.out.write("Agent;%s;%i;%s;%i\n" % (ask.source.__str__(), ask.source.cash, self.name, ask.source.assets[self.name]))
            if ask.source != bid.source: # Pour ne pas afficher deux fois la même ligne si l'agent ayant émis le ask et celui ayant émis le bid est le même.
                market.out.write("Agent;%s;%i;%s;%i\n" % (bid.source.__str__(), bid.source.cash, self.name, bid.source.assets[self.name]))
        return self.last_transaction


class Market:
    def __init__(self, out=sys.stdout, print_orderbooks=False):
        self.time = 0
        self.traders = []
        self.orderbooks = dict()
        self.prices = dict()
        self.all_prices = dict() # Contient la liste des prix pris par chaque asset à chaque fin de tick
        self.out = out
        self.print_ob = print_orderbooks
        self.print_agent = True
        self.nb_order_sent = 0
        self.nb_fixed_price = 0
        self.out.write("# LimitOrder;asset;agent;direction;price;qty\n# CancelOrder;asset;agent\n# Tick;nb_tick\n# or Tick;nb_tick;asset;last_price\n# Price;asset;bider;asker;price;qty\n# Agent;name;cash;last_modified_asset;qty\n\n")
    def __str__(self):
        return "Market with %i traders on assets: %s" % (len(self.traders), str(self.orderbooks.keys()))
    def add_asset(self, orderbook):
        self.orderbooks[orderbook.name] = orderbook
        self.prices[orderbook.name] = None
        self.all_prices[orderbook.name] = []
    def remove_asset(self, orderbook):
        self.orderbooks.pop(orderbook.name, None)
        self.prices.pop(orderbook.name, None)
        self.all_prices.pop(orderbook.name, None)
    def add_trader(self, trader):
        if not trader in self.traders:
            self.traders.append(trader)
    def remove_trader(self, trader):
        self.traders.remove(trader)
    def print_state(self):
        self.out.write("\n# Nb orders received: %i\n# Nb fixed prices: %i\n# Leaving ask size: %i\n# Leaving bid size: %i\n" % (self.nb_order_sent, self.nb_fixed_price, sum([self.orderbooks[asset].asks.size for asset in self.orderbooks.keys()]), sum([self.orderbooks[asset].bids.size for asset in self.orderbooks.keys()])))
    def update_time(self):
        self.time += 1
        at_least_one_price = False
        for asset in self.orderbooks.keys():
            if self.prices[asset] != None:
                at_least_one_price = True
                self.out.write("Tick;%i;%s;%i\n" % (self.time, asset, self.prices[asset]))
                self.all_prices[asset].append(self.prices[asset])
        if not(at_least_one_price):
            self.out.write("Tick;%i\n" % self.time)
        if self.print_ob:
            for ob in self.orderbooks.keys():
                self.out.write(self.orderbooks[ob].__str__())
    def run_once(self, suffle=True):
        if suffle:
            random.shuffle(self.traders)
        for t in self.traders:
            decision = t.place_order(self)
            if decision != None:
                if decision.asset in self.orderbooks:
                    self.orderbooks[decision.asset].add_order(decision, self)
        self.update_time()
    def replay(self, filename):
        '''Run a list of orders of the form Order;asset;direction;price;qty).'''
        t = Trader(self.orderbooks.keys())
        self.print_agent = False
        self.add_trader(t)
        with open(filename, 'r') as file:
            for line in file:
                l = line.split(";")
                if l[0] == "Order":
                    self.orderbooks[l[1]].add_order(LimitOrder(l[1], t, l[2], int(l[3]), int(l[4])), self)
        self.print_agent = True
    def generate(self, assets, nb_agent, nb_turn):
        for asset in assets:
            self.add_asset(OrderBook(asset))
        for i in range(nb_agent):
            self.add_trader(ZITTrader(assets))
        for i in range(nb_turn):
            self.run_once()