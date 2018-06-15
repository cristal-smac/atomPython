#!/usr/bin/python

from atom import *

out = open('trace.dat', 'w')
m = Market(out, print_orderbooks=True)
m.add_asset(OrderBook('Apple'))

for i in range(10):
    t = ZITTrader(['Apple'], [10])
    m.add_trader(t)
for i in range(10):
    m.run_once()

out.close()

Prices = process_prices_per_tick('trace.dat')
# process_prices_per_tick prend un nom de fichier, le lit, et retourne un dictionnaire dont les clés sont les assets
# et les valeurs un tuple de listes : la première contient les différents tick et la second, le dernier prix prit par 
# l'asset à chaque tick
for asset in Prices.keys():
    plt.plot(Prices[asset][0], Prices[asset][1], '-', label=asset)
plt.legend(loc='best')
plt.xlabel('Tick')
plt.ylabel('Price')
plt.show()