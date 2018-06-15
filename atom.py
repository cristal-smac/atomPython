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
# (1) Ajouter une trace des ordres, prix et agents
# (2) Vérifier s'il y a des matchs à chaque rajout d'ordre, pas une fois que tous les ordres ont été rajoutés
# (3) Modifier le prix du match comme étant le prix le plus ancien
# (4) Modification des ZIT pour qu'ils ne puissent plus avoir une quantité d'actions négative
# (5) Utilisation de MinHeap et MaxHeap pour OrderBook.asks et OrderBook.bids plutôt que des listes triées. Si n est la taille du carnet d'ordre, l'ajout d'ordre se faisait en O(nlog n), maintenant il se fait en O(log n). Pour 20 agents et 2000 ticks, on passe d'un temps d'exécution de 24s à 2.6s.
# (6) Revenir sur la modification des ZIT : la solution choisie a l'air très coûteuse en temps (on doit parcourir l'orderbook à chaque fois...) alors que si on garde en mémoire un entier égal au nombre d'actions concernées par un BID, on augmente la complexité spatialle seulement de (nb agent * nb asset) et il n'y a plus de lourd calcul à faire (il faut juste penser, à chaque fois qu'on a un match, à updater cette quantité)...
#   C'est implémenté... En pratique, le temps de calcul n'est pas changé même pour un grand nombre d'agents et de ticks... Je ne comprends pas pourquoi. Peut-être que Python optimise les calculs faits dans la version précédente. 
# (7) Ajouter une option pour pouvoir balancer la trace dans un fichier trace.dat plutôt que dans le out.writeer (utile pour utiliser ensuite atom dans Jupyter...)
#
# TODO :
#
# - Refaire les méthodes __str__
# - Ajouter des méthodes qui renvoient directement les données 'traitées' à partir d'un fichier (trace.dat), puisque c'est assez "lourd".

import random
import sys
import pylab as plt
import numpy as np
import pandas as pd

import binary_heap as bh
from data_processing import *


class LimitOrder:
    def __init__(self, asset, source, direction, price, qty, time_to_live=None):
        self.asset = asset
        self.source = source
        self.price = price
        self.direction = direction.upper()
        self.qty = qty
        self.time_to_live = time_to_live
    def __str__(self):
        if self.time_to_live == None:
            return "%s %s at %.2f x %i from %s (life: immortal)" % (self.direction, self.asset, self.price, self.qty, self.source.trader_id)
        else:
            return "%s %s at %.2f x %i from %s (life: %i)" % (self.direction, self.asset, self.price, self.qty, self.source.trader_id, self.time_to_live)
    def decrease_qty(self, q):
        self.qty -= q
    def attribute_list(self):
        return [self.asset, self.source.__str__(), self.direction, self.price, self.qty, self.time_to_live]
    def decrease_life(self):
        if self.time_to_live != None:
            self.time_to_live -= 1
    def is_dead(self):
        return self.time_to_live == 0


class Trader(object):
    trader_count = 0
    def __init__(self, available_assets=[], initial_assets=None, money=0):
        Trader.trader_count += 1
        self.trader_id = Trader.trader_count
        self.money = money
        self.available_assets = available_assets
        self.assets = dict()
        self.invested_assets = dict()
        if initial_assets == None:
            initial_assets = [0]*len(available_assets)
        for cpt, asset in enumerate(available_assets):
            self.assets[asset] = initial_assets[cpt]
            self.invested_assets[asset] = 0
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
            q = self.assets[asset] - self.invested_assets[asset] # self.invested_assets[asset] = sum([order.qty for order in market.orderbooks[asset].asks.values() if order.source == self and order.direction == 'ASK']) -> cf commentaire (6)
            if q > 0:
                s_assets[asset] = q
        return s_assets
    def place_order(self, market):
        s_assets = self.sellable_assets(market)
        price = random.randint(1, 100)
        if bool(s_assets): # si s_assets n'est pas vide
            # Si on a encore qqchose à vendre, on choisi aléatoirement entre achat et vente
            dir = random.choice(['ASK', 'BID'])
            asset = random.choice(self.available_assets)
            if dir == 'BID':
                return LimitOrder(asset, self, 'BID', price, random.randint(1, min(100, market.total_nb_stock[asset])), random.randint(1, 5))
            else:
                asset = random.choice(list(s_assets.keys()))
                # On ne vend pas une qté > à celle qu'on peut vendre, et jamais plus que 100.
                return LimitOrder(asset, self, 'ASK', price, random.randint(1, min(100,s_assets[asset])), random.randint(1, 5))
        else:
            # On ne peut rien vendre -> on achète
            asset = random.choice(self.available_assets)
            return LimitOrder(asset, self, 'BID', price, random.randint(1, min(100, market.total_nb_stock[asset])), random.randint(1, 5))


class ZITTraderWithNegQty(Trader):
    def __str__(self):
        return "ZIT " + super().__str__()
    def place_order(self, market):
        return LimitOrder(random.choice(self.available_assets), self, random.choice(['ASK', 'BID']), random.randint(1, 100), random.randint(1, 100))


class OrderBook:
    def __init__(self, name):
        self.name = name
        self.bids = bh.MaxHeap(lambda x: x.price)
        self.asks = bh.MinHeap(lambda x: x.price)
        self.last_transaction = None
    def __str__(self):
        Asks = "" ; Bids = ""
        l_a = [o for o in self.asks.tree if o.time_to_live == None or o.time_to_live > 0] ; l_a.sort(key=(lambda x: x.price))
        l_b = [o for o in self.bids.tree if o.time_to_live == None or o.time_to_live > 0] ; l_b.sort(key=(lambda x: -x.price))
        for order in l_a:
            Asks += order.__str__()+"\n"
        for order in l_b:
            Bids += order.__str__()+"\n"
        return "OrderBook "+self.name+":\nAsks:\n"+Asks+"Bids:\n"+Bids
    def add_order(self, order, market):
        if order.direction == "BID":
            self.add_bid(order)
        else:
            self.add_ask(order)
        lst = order.attribute_list()
        if lst[-1] == None:
            market.out.write("Order;%s;%s;%s;%i;%i\n" % tuple(lst[:-1]))
        else:
            market.out.write("Order;%s;%s;%s;%i;%i;%i\n" % tuple(lst))
        while self.match(order.direction, market) != None:
            pass
    def add_bid(self, order):
        self.bids.insert(order)
    def add_ask(self, order):
        self.asks.insert(order)
        order.source.invested_assets[self.name] += order.qty
    def decrease_life(self):
        for order in self.asks.tree:
            order.decrease_life()
        for order in self.bids.tree:
            order.decrease_life()
        # On a diminué la vie de chaque ordre. Dans l'idéal, il faudrait virer tous les ordres "morts" (time_to_live = 0), mais la structure adoptée pour asks et bids
        # (tas binaires) fait que ce n'est pas faisable de façon efficaces : les ordres morts peuvent être n'import où dans le tas...
        # A la place, quand on va faire un match, on va retirer tous les ordres morts sur lesquels on tombe quand on va prendre le plus petit élement des tas...
    def match(self, dir, market): # Si une transaction est possible, l'effectue, sachant que le dernier ordre ajouté a pour direction dir. Sinon, retourne None.
        while self.asks.size > 0 and self.asks.root().is_dead():
            ask = self.asks.extract_root()
            ask.source.invested_assets[self.name] -= ask.qty
        while self.bids.size > 0 and self.bids.root().is_dead():
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
        ask.source.add_money(price*qty)
        ask.source.add_assets(self.name, -qty)
        ask.source.invested_assets[self.name] -= qty
        bid.source.add_money(-price*qty)
        bid.source.add_assets(self.name, qty)
        self.last_transaction = (bid.source, ask.source, price, qty)
        market.prices[self.name] = price
        # On affiche le prix
        market.out.write("Price;%s;%s;%s;%i;%i\n" % (self.name, bid.source.__str__(), ask.source.__str__(), price, qty))
        # On affiche les agents qui ont été modifiés
        market.out.write("Agent;%s;%i;%s;%i\n" % (ask.source.__str__(), ask.source.money, self.name, ask.source.assets[self.name]))
        if ask.source != bid.source: # Pour ne pas afficher deux fois la même ligne si l'agent ayant émis le ask et celui ayant émis le bid est le même.
            market.out.write("Agent;%s;%i;%s;%i\n" % (bid.source.__str__(), bid.source.money, self.name, bid.source.assets[self.name]))
        return self.last_transaction


class Market:
    def __init__(self, out=None, print_orderbooks=False):
        self.time = 0
        self.traders = []
        self.orderbooks = dict()
        self.total_nb_stock = dict()
        self.prices = dict()
        self.out = sys.stdout if out == None else out
        self.print_ob = print_orderbooks
    def __str__(self):
        return "Market with %i traders on assets: %s" % (len(self.traders), str(self.orderbooks.keys()))
    def add_asset(self, orderbook):
        self.orderbooks[orderbook.name] = orderbook
        self.prices[orderbook.name] = None
        self.total_nb_stock[orderbook.name] = 0
    def remove_asset(self, orderbook):
        self.orderbooks.pop(orderbook.name, None)
        self.prices.pop(orderbook.name, None)
        self.total_nb_stock.pop(orderbook.name, None)
    def add_trader(self, trader):
        if not trader in self.traders:
            self.traders.append(trader)
        for asset in self.total_nb_stock.keys():
            self.total_nb_stock[asset] += trader.assets[asset]
    def remove_trader(self, trader):
        self.traders.remove(trader)
        for asset in self.total_nb_stock.keys():
            self.total_nb_stock[asset] -= trader.assets[asset]
    def update_time(self):
        self.time += 1
        at_least_one_price = False
        for asset in self.orderbooks.keys():
            if self.prices[asset] != None:
                at_least_one_price = True
                self.out.write("Tick;%i;%s;%i\n" % (self.time, asset, self.prices[asset]))
        if not(at_least_one_price):
            self.out.write("Tick;%i\n" % self.time)
        for ob in self.orderbooks.keys():
            self.orderbooks[ob].decrease_life()
            if self.print_ob:
                self.out.write(self.orderbooks[ob].__str__())
    def run_once(self):
        random.shuffle(self.traders)
        for t in self.traders:
            decision = t.place_order(self)
            if decision != None:
                if decision.asset in self.orderbooks:
                    self.orderbooks[decision.asset].add_order(decision, self)
        self.update_time()
    def replay(self, order_list):
        '''Run a list of orders of the form (asset, direction, price, qty).'''
        t = Trader(self.orderbooks.keys())
        m.add_trader(t)
        for o in order_list:
            self.time += 1
            asset, direction, price, qty = o
            order = LimitOrder(asset, t, direction, price, qty)
            self.orderbooks[asset].add_order(order, self)