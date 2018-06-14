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
# DONE :
#
# - Ajouter une trace des ordres, prix et agents
# - Vérifier s'il y a des matchs à chaque rajout d'ordre, pas une fois que tous les ordres ont été rajoutés
# - Modifier le prix du match comme étant le prix le plus ancien
# - Modification des ZIT pour qu'ils ne puissent plus avoir une quantité d'actions négative
#
# TODO :
#
# - Regarder s'il existe un équivalent des TreeSet (Java) en Python pour les Orderbooks.asks/bids : on n'a besoin que des meilleurs éléments de la liste, pas d'avoir une liste entièrement (utiliser un tas-min et un tas-max ?)

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
    def __init__(self, available_assets=[], initial_assets=None, money=0):
        Trader.trader_count += 1
        self.trader_id = Trader.trader_count
        self.money = money
        self.available_assets = available_assets
        self.assets = dict()
        if initial_assets == None:
            initial_assets = [0]*len(available_assets)
        for cpt, asset in enumerate(available_assets):
            self.assets[asset] = initial_assets[cpt]
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
    def sellable_assets(self, market):
        s_assets = dict()
        for asset in self.available_assets:
            # Quantité d'actions vendable = quantité d'actions dont on dispose moins la quantité d'actions déjà inclues dans un ordre BID pour cet asset.
            q = self.assets[asset] - sum([order.qty for order in market.orderbooks[asset].asks if order.source == self and order.direction == 'ASK'])
            if q > 0:
                s_assets[asset] = q
        return s_assets
    def place_order(self, market):
        s_assets = self.sellable_assets(market)
        if bool(s_assets): # si s_assets n'est pas vide
            # Si on a encore qqchose à vendre, on choisi aléatoirement entre achat et vente
            dir = random.choice(['ASK', 'BID'])
            if dir == 'BID':
                return LimitOrder(random.choice(self.available_assets), self, 'BID', random.randint(1, 100), random.randint(1, 100))
            else:
                asset = random.choice(list(s_assets.keys()))
                # On ne vend pas une qté > à celle qu'on peut vendre, et jamais plus que 100.
                return LimitOrder(asset, self, 'ASK', random.randint(1, 100), random.randint(1, min(100, s_assets[asset])))
        else:
            # On ne peut rien vendre -> on achète
            asset = random.choice(self.available_assets)
            return LimitOrder(asset, self, 'BID', random.randint(1, 100), random.randint(1, 100))


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
        while self.match(order.direction, market) != None:
            pass
    def add_bid(self, order):
        self.bids.append(order)
        self.bids.sort(key=lambda o: -o.price)
    def add_ask(self, order):
        self.asks.append(order)
        self.asks.sort(key=lambda o: o.price)
    def match(self, dir, market): # Si une transaction est possible, l'effectue, sachant que le dernier ordre ajouté a pour direction dir. Sinon, retourne None.
        if (len(self.asks) == 0) | (len(self.bids) == 0):
            return None
        if self.asks[0].price > self.bids[0].price:
            return None
        ask = self.asks.pop(0)
        bid = self.bids.pop(0)
        qty = min(ask.qty, bid.qty)
        price = bid.price if dir == 'ASK' else ask.price # Prend le prix de l'ordre le plus ancien
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
    def replay(self, order_list):
        '''Run a list of orders of the form (asset, direction, price, qty).'''
        t = Trader(self.orderbooks.keys())
        m.add_trader(t)
        for o in order_list:
            self.time += 1
            asset, direction, price, qty = o
            order = LimitOrder(asset, t, direction, price, qty)
            self.orderbooks[asset].add_order(order, self)