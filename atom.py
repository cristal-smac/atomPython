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

class LimitOrder:
    def __init__(self, asset, source, direction, price, qty, time_to_live=None):
        self.asset = asset
        self.source = source
        self.price = price
        self.direction = direction.upper()
        self.qty = qty
        self.time_to_live = time_to_live
    def __str__(self):
        return "%s %s at %.2f x %i from %s" % (self.direction, self.asset, self.price, self.qty, self.source.trader_id)
    def decrease_qty(self, q):
        self.qty -= q
    def decrease_life(self):
        if self.time_to_live != None:
            self.time_to_live -= 1
    def is_dead(self):
        return self.time_to_live == 0

    
class Trader(object):
    trader_count = 0
    def __init__(self, available_assets=[]):
        Trader.trader_count += 1
        self.trader_id = Trader.trader_count
        self.assets = dict()
        self.available_assets = available_assets
    def __str__(self):
        return str(self.trader_id)
    def make_available(self, asset):
        available_assets.append(asset)
    def remove(self, asset):
        available_assets.remove(asset)
    def place_order(self, market):
        raise NotImplementedException
    

class ZITTrader(Trader):
    def __str__(self):
        return "ZIT " + super().__str__()
    def place_order(self, market):
        asset = random.choice(self.available_assets)
        return LimitOrder(asset, self, random.choice(['ASK', 'BID']), random.randint(1, 100), random.randint(1, 100), random.randint(1, 5))


class OrderBook:
    def __init__(self, name):
        self.name = name
        self.bids = []
        self.asks = []
        self.last_transaction = None
    def __str__(self):
        return self.name + "\n" + str([str(x) for x in self.bids]) + "\n" + str([str(x) for x in self.bids])
    def update_timer(self):
        for o in self.asks:
            o.decrease_life()
        self.asks = [o for o in self.asks if not o.is_dead()]
        for o in self.bids:
            o.decrease_life()
        self.bids = [o for o in self.bids if not o.is_dead()]        
    def add_order(self, order):
        if order.direction == "BID":
            self.add_bid(order)
        else:
            self.add_ask(order)
    def add_bid(self, order):
        self.bids.append(order)
        self.bids.sort(key=lambda o: -o.price)
    def add_ask(self, order):
        self.asks.append(order)
        self.asks.sort(key=lambda o: o.price)
    def match(self):
        if (len(self.asks) == 0) | (len(self.bids) == 0):
            return None
        if self.asks[0].price > self.bids[0].price:
            return None
        ask = self.asks.pop(0)
        bid = self.bids.pop(0)
        qty = min(ask.qty, bid.qty)
        price = bid.price
        if ask.qty > qty:
            ask.decrease_qty(qty)
            self.asks.insert(0, ask)
        if bid.qty > qty:
            bid.decrease_qty(qty)
            self.bids.insert(0, bid)
        self.last_transaction = (bid.source, ask.source, price, qty)
        return self.last_transaction


class Market:
    def __init__(self):
        self.traders = []
        self.orderbooks = dict()
        self.time = 0
        self.prices = dict()
    def __str__(self):
        return "Market with %i traders on assets: %s" % (len(self.traders), str(self.orderbooks.keys()))
    def add_asset(self, orderbook):
        self.orderbooks[orderbook.name] = orderbook
        self.prices[orderbook.name] = []
    def remove_asset(self, orderbook):
        self.orderbooks.pop(orderbook.name, None)
        self.prices.pop(orderbook.name, None)
    def add_trader(self, trader):
        if not trader in self.traders:
            self.traders.append(trader)
    def remove_trader(self, trader):
        self.traders.remove(trader)
    def run_once(self):
        self.time += 1
        prices = []
        random.shuffle(self.traders)
        for t in self.traders:
            decision = t.place_order(self)
            if decision != None:
                if decision.asset in self.orderbooks:
                    self.orderbooks[decision.asset].add_order(decision)
        for o in self.orderbooks.values():
            o.last_transaction = None
            while o.match() != None:
                pass
            o.update_timer()
            if o.last_transaction != None:
                self.prices[o.name].append(o.last_transaction[2])        
                prices.append((o.name, self.time, o.last_transaction[2]))
        return prices

