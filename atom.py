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

#
# TODO :
#
# - Vérifier s'il y a des matchs à chaque rajout d'ordre, pas une fois que tous les ordres ont été rajoutés ?
# - Corollaire : Modifier le prix du match comme étant le prix le plus ancien
# - Regarder s'il existe un équivalent des TreeSet (Java) en Python pour les Orderbooks.asks/bids : on n'a besoin que des meilleurs éléments de la liste, pas d'avoir une liste entièrement triée

import random
import pylab as plt
import numpy as np
import pandas as pd
import matplotlib.mlab as mlab


class LimitOrder:
    def __init__(self, asset, source, direction, price, qty):
        self.asset = asset
        self.source = source
        self.price = price
        self.direction = direction.upper()
        self.qty = qty
    def __str__(self):
        return "%s %s at %.2f x %i from %s" % (self.direction, self.asset, self.price, self.qty, self.source.trader_id)
    def decrease_qty(self, q):
        self.qty -= q
    def attribute_list(self):
        return [self.asset, self.source.__str__(), self.direction, self.price, self.qty]


class Trader(object):
    trader_count = 0
    def __init__(self, available_assets=[], money=0, auto=False):
        Trader.trader_count += 1
        self.trader_id = Trader.trader_count
        self.money = money
        self.available_assets = available_assets
        self.assets = dict()
        for a in available_assets:
            self.assets[a] = 0
    def __str__(self):
        return str(self.trader_id)
    def make_available(self, asset):
        available_assets.append(asset)
        self.assets[asset] = 0
    def remove(self, asset):
        available_assets.remove(asset)
        self.assets.pop(asset)
    def place_order(self, market):
        raise NotImplementedException
    def add_money(self, n):
        self.money += n
    def add_assets(self, asset, n):
        self.assets[asset] += n
    

class ZITTrader(Trader):
    def __str__(self):
        return "ZIT " + super().__str__()
    def place_order(self, market):
        asset = random.choice(self.available_assets)
        return LimitOrder(asset, self, random.choice(['ASK', 'BID']), random.randint(1, 100), random.randint(1, 100))


class OrderBook:
    def __init__(self, name):
        self.name = name
        self.bids = []
        self.asks = []
        self.last_transaction = None
    def __str__(self):
        return self.name + "\n" + str([str(x) for x in self.asks]) + "\n" + str([str(x) for x in self.bids])
    def add_order(self, order, market):
        if order.direction == "BID":
            self.add_bid(order)
        else:
            self.add_ask(order)
        print("Order;%s;%s;%s;%i;%i" % tuple(order.attribute_list()))
    def add_bid(self, order):
        self.bids.append(order)
        self.bids.sort(key=lambda o: -o.price)
    def add_ask(self, order):
        self.asks.append(order)
        self.asks.sort(key=lambda o: o.price)
    def match(self, market): # Si une transaction est possible, l'effectue. Sinon, retourne None.
        if (len(self.asks) == 0) | (len(self.bids) == 0):
            return None
        if self.asks[0].price > self.bids[0].price:
            return None
        ask = self.asks.pop(0)
        bid = self.bids.pop(0)
        qty = min(ask.qty, bid.qty)
        price = bid.price # TODO : à changer
        if ask.qty > qty:
            ask.decrease_qty(qty)
            self.asks.insert(0, ask)
        if bid.qty > qty:
            bid.decrease_qty(qty)
            self.bids.insert(0, bid)
        # On modifie les agents
        ask.source.add_money(price*qty)
        ask.source.add_assets(self.name, -qty)
        bid.source.add_money(-price*qty)
        bid.source.add_assets(self.name, qty)
        self.last_transaction = (bid.source, ask.source, price, qty)
        market.prices[self.name] = price
        # On affiche le prix
        print("Price;%s;%s;%s;%i;%i" % (self.name, bid.source.__str__(), ask.source.__str__(), price, qty))
        # On affiche les agents qui ont été modifiés
        print("Agent;%s;%i;%s;%i" % (ask.source.__str__(), ask.source.money, self.name, ask.source.assets[self.name]))
        if ask.source != bid.source: # Pour ne pas afficher deux fois la même ligne si l'agent ayant émis le ask et celui ayant émis le bid est le même.
            print("Agent;%s;%i;%s;%i" % (bid.source.__str__(), bid.source.money, self.name, bid.source.assets[self.name]))
        return self.last_transaction


class Market:
    def __init__(self):
        self.time = 0
        self.traders = []
        self.orderbooks = dict()
        self.prices = dict()
    def __str__(self):
        return "Market with %i traders on assets: %s" % (len(self.traders), str(self.orderbooks.keys()))
    def add_asset(self, orderbook):
        self.orderbooks[orderbook.name] = orderbook
        self.prices[orderbook.name] = None
    def remove_asset(self, orderbook):
        self.orderbooks.pop(orderbook.name, None)
        self.prices.pop(orderbook.name, None)
    def add_trader(self, trader):
        if not trader in self.traders:
            self.traders.append(trader)
    def remove_trader(self, trader):
        self.traders.remove(trader)
    def update_time(self):
        self.time += 1
        at_least_one_price = False
        for asset in self.orderbooks.keys():
            if self.prices[asset] != None:
                at_least_one_price = True
                print("Tick;%i;%s;%i" % (self.time, asset, self.prices[asset]))
        if not(at_least_one_price):
            print("Tick;%i" % self.time)
    def run_once(self):
        self.update_time()
        random.shuffle(self.traders)
        # Modifier la suite ?
        # Ne devrait-on pas vérifier s'il y a des match après chaque ajout d'ordre ?
        for t in self.traders:
            decision = t.place_order(self)
            if decision != None:
                if decision.asset in self.orderbooks:
                    self.orderbooks[decision.asset].add_order(decision, self)
        for ob in self.orderbooks.values():
            ob.last_transaction = None
            while ob.match(self) != None:
                pass
    def replay(self, order_list):
        '''Run a list of orders of the form (asset, direction, price, qty).'''
        t = Trader(self.orderbooks.keys())
        m.add_trader(t)
        for o in order_list:
            self.time += 1
            asset, direction, price, qty = o
            order = LimitOrder(asset, t, direction, price, qty)
            self.orderbooks[asset].add_order(order, self)
            for ob in self.orderbooks.values():
                ob.last_transaction = None
                while ob.match(self) != None:
                    pass