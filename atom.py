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
        self.time = None
        self.canceled = False
    def __str__(self):
        return "LimitOrder;%s;%s;%s;%i;%i" % (self.asset, self.source.__str__(), self.direction, self.price, self.qty)
    def decrease_qty(self, q):
        self.qty -= q
    def attribute_list(self):
        return [self.asset, self.source.__str__(), self.direction, self.price, self.qty]
    def cancel(self):
        self.canceled = True
    def current_time(self, market):
        self.time = int(time.time()*1000000-market.t0)

class CancelMyOrders(Order):
    def __str__(self):
        return "CancelMyOrders;%s;%s" % (self.asset, self.source.__str__())


class Trader(object):
    trader_count = 0
    def __init__(self, market, initial_assets=None, cash=0):
        Trader.trader_count += 1
        self.trader_id = Trader.trader_count
        self.cash = cash
        self.assets = dict()
        if initial_assets == None:
            initial_assets = [0]*len(market.orderbooks.keys())
        for asset in market.orderbooks.keys():
            self.assets[asset] = initial_assets[list(market.orderbooks.keys()).index(asset)]
    def __str__(self):
        return str(self.trader_id)
    def decide_order(self, market, asset):
        raise NotImplementedException
    def add_cash(self, n):
        self.cash += n
    def add_assets(self, asset, n):
        self.assets[asset] += n
    def get_wealth(self, market):
        '''init_price: valeur supposée d'un asset quand aucun prix n'a encore été fixé '''
        w = self.cash
        for asset in market.orderbooks.keys():
            w += self.assets[asset]*(market.prices[asset] if market.prices[asset] != None else market.init_price)
        return w
    def get_infos(self, market):
        s = self.__str__()+":\nCash: "+str(self.cash)+"\n"
        for asset in market.orderbooks.keys():
            s += asset+": "+str(self.assets[asset])+"\n"
        s += "Wealth: "+str(self.get_wealth(market))+"\n"
        return s

class DumbAgent(Trader):
    def __str__(self):
        return "Dumby "+super().__str__()
    def decide_order(self, market, asset):
        return None
    def send_order(self, order, market):
        market.orderbooks[order.asset].add_order(order, market)


class ZITTrader(Trader):
    def __init__(self, market, initial_assets=None, cash=0, p_min=1000, p_max=9999, q_min=1, q_max=9, pb_ask=.5, pb_bid=.5):
        Trader.__init__(self, market, initial_assets, cash)
        self.pb_ask = pb_ask # Probabilité d'envoyer un ask
        self.pb_bid = pb_bid # Probabilité d'envoyer un bid
        self.p_min = p_min
        self.p_max = p_max
        self.q_min = q_min
        self.q_max = q_max
    def __str__(self):
        return "ZIT " + super().__str__()
    def decide_order(self, market, asset):
        r = random.random() # 0 <= r < 1
        if r <= self.pb_ask+self.pb_bid:
            return LimitOrder(asset, self, 'ASK' if r <= self.pb_ask else 'BID', random.randint(self.p_min, self.p_max), random.randint(self.q_min, self.q_max))
        else:
            return None

class OrderBook:
    def __init__(self, name):
        self.name = name
        self.asks = bh.MinHeap(lambda x: (x.price, x.time))
        self.bids = bh.MaxHeap(lambda x: (x.price, -x.time))
        self.last_transaction = None
    def __str__(self):
        Asks = "" ; Bids = ""
        l_a = self.asks.tree[:] ; l_a.sort(key=(lambda x: (x.price, x.time)))
        l_b = self.bids.tree[:] ; l_b.sort(key=(lambda x: (-x.price, x.time)))
        for order in l_a:
            Asks += "\t"+order.__str__()+"\n"
        for order in l_b:
            Bids += "\t"+order.__str__()+"\n"
        return "OrderBook "+self.name+":\nAsks:\n"+(Asks if Asks != "" else "\tEmpty\n")+"Bids:\n"+(Bids if Bids != "" else "\tEmpty\n")
    def add_order(self, order, market):
        market.nb_order_sent += 1
        market.write(order.__str__()+"\n")
        if type(order).__name__ == 'LimitOrder':
            order.current_time(market)
            if order.direction == "BID":
                self.add_bid(order)
            else:
                self.add_ask(order)
            if market.print_ob:
                market.write(market.orderbooks[self.name].__str__())
            while self.match(order.direction, market) != None:
                pass
        elif type(order).__name__ == 'CancelMyOrders':
            for o in self.asks.tree:
                if o.source == order.source:
                    o.cancel()
            for o in self.bids.tree:
                if o.source == order.source:
                    o.cancel()
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
        market.write("Price;%s;%s;%s;%i;%i;%i\n" % (self.name, bid.source.__str__(), ask.source.__str__(), price, qty, int(time.time()*1000000-market.t0)))
        if market.print_ob:
            market.write(market.orderbooks[self.name].__str__())
        market.nb_fixed_price += 1
        # On affiche les agents qui ont été modifiés
        market.write("Agent;%s;%i;%s;%i;%i\n" % (ask.source.__str__(), ask.source.cash, self.name, ask.source.assets[self.name], int(time.time()*1000000-market.t0)))
        if ask.source != bid.source: # Pour ne pas afficher deux fois la même ligne si l'agent ayant émis le ask et celui ayant émis le bid est le même.
            market.write("Agent;%s;%i;%s;%i;%i\n" % (bid.source.__str__(), bid.source.cash, self.name, bid.source.assets[self.name], int(time.time()*1000000-market.t0)))
        # À chaque fois qu'un prix est fixé, le wealth de TOUS les agents est modifié. On les affiche donc tous.
        for agent in market.traders:
            market.write("AgentWealth;%s;%i;%i\n" % (agent.__str__(), agent.get_wealth(market), int(time.time()*1000000-market.t0)))
        return self.last_transaction


class Market:
    def __init__(self, list_assets, out=sys.stdout, print_orderbooks=False, init_price=0, hist_len=100):
        # init_price : prix initial supposé des différents cours quand a aucun prix n'a encore été fixé (surtout utilisé pour le calcul du wealth)
        # hist_len : à un asset donné, nombre de prix gardés en mémoire par le marché
        self.t0 = time.time()*1000000
        self.time = 0
        self.traders = []
        self.orderbooks = dict()
        self.prices = dict()
        self.prices_hist = dict() # Contient l'historique des prix pris par chaque asset à chaque fin de tick
        self.out = out
        self.out_type = 'file' if type(out).__name__ == 'TextIOWrapper' or type(out).__name__ == 'OutStream' else 'None'
        self.print_ob = print_orderbooks
        self.nb_order_sent = 0
        self.nb_fixed_price = 0
        self.init_price = init_price
        self.hist_len = hist_len
        self.write("# LimitOrder;asset;agent;direction;price;qty\n# CancelMyOrders;asset;agent\n# Tick;nb_tick\n# Price;asset;bider;asker;price;qty;timestamp(µs)\n# NewAgent;name;cash;asset 1:qty 1,...,asset n:qty n\n# Agent;name;cash;last_modified_asset;qty\n# AgentWealth;agent;wealth;timestamp(µs)\n\n")
        for asset in list_assets:
            orderbook = OrderBook(asset)
            self.orderbooks[orderbook.name] = orderbook
            self.prices[orderbook.name] = None
            self.prices_hist[orderbook.name] = []
    def __str__(self):
        return "Market with %i traders on assets: %s" % (len(self.traders), str(self.orderbooks.keys()))
    def write(self, s):
        if self.out_type == 'file':
            self.out.write(s)
    def add_trader(self, trader):
        if not trader in self.traders:
            self.traders.append(trader)
            s = ""
            for asset in self.orderbooks.keys():
                if s != "":
                    s += ","
                s += asset + ":" + str(trader.assets[asset])
            self.write("NewAgent;%s;%i;%s\n" % (trader.__str__(), trader.cash, s))
            self.write("AgentWealth;%s;%i;%i\n" % (trader.__str__(), trader.get_wealth(self), int(time.time()*1000000-self.t0)))
    def remove_trader(self, trader):
        self.traders.remove(trader)
    def print_state(self):
        self.write("\n# Nb orders received: %i\n# Nb fixed prices: %i\n# Leaving ask size: %i\n# Leaving bid size: %i\n" % (self.nb_order_sent, self.nb_fixed_price, sum([self.orderbooks[asset].asks.size for asset in self.orderbooks.keys()]), sum([self.orderbooks[asset].bids.size for asset in self.orderbooks.keys()])))
    def print_last_prices(self):
        for asset in self.orderbooks.keys():
            self.write("Price;%s;None;None;%i;None;%i\n" % (asset, self.prices[asset], int(time.time()*1000000-self.t0)))
    def update_time(self):
        self.time += 1
        for asset in self.orderbooks.keys():
            if self.prices[asset] != None:
                self.prices_hist[asset].append(self.prices[asset])
                if len(self.prices_hist[asset]) > self.hist_len:
                    self.prices_hist[asset].pop(0)
        self.write("Tick;%i\n" % self.time)
    def run_once(self, suffle=True):
        if suffle:
            random.shuffle(self.traders)
        # Au sein d'un tour, chaque agent a exactement une fois la possibilité d'envoyer un ordre pour chaque asset
        for t in self.traders:
            for asset in self.orderbooks.keys():
                decision = t.decide_order(self, asset)
                if decision != None:
                    self.orderbooks[decision.asset].add_order(decision, self)
        self.update_time()
    def generate(self, nb_agent, nb_turn, init_assets=0, init_cash=0):
        for i in range(nb_agent):
            self.add_trader(ZITTrader(self, [init_assets]*len(self.orderbooks.keys()), init_cash))
        for i in range(nb_turn):
            self.run_once()
    def replay(self, filename):
        # Modifier toute cette merde !!! (ne fonctionne plus à cause du retrait de available_assets)
        traders = dict() # Dictionnaire qui associe à chaque agent lu dans la trace un agent automate
        with open(filename, 'r') as file:
            for line in file:
                l = line.split(';')
                if l[0] == 'NewAgent':
                    ias = l[3].split(',') # Liste des strings initial assets
                    ia = [int(ias[i].split(':')[1]) for i in range(len(ias))]
                    t = Trader(self, ia, int(l[2]))
                    traders[l[1]] = t
                    self.add_trader(t)
                elif l[0] == 'LimitOrder':
                    self.orderbooks[l[1]].add_order(LimitOrder(l[1], traders[l[2]], l[3], int(l[4]), int(l[5])), self)
                elif l[0] == 'CancelMyOrders':
                    self.orderbooks[l[1]].add_order(CancelMyOrders(l[1], traders[l[2]]), self)