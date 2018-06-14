#!/usr/bin/python

from atom import *

m = Market()
m.add_asset(OrderBook('Apple'))
m.add_asset(OrderBook('Microsoft'))

for i in range(20):
    t = ZITTrader(['Apple'], [50])
    m.add_trader(t)
for i in range(2000):
    m.run_once()

## Test replay

# m = Market(True, True, False)
# m.add_asset(OrderBook('Apple'))

# m.replay([('Apple', 'ASK', 50, 10, None), ('Apple', 'ASK', 40, 10, None), ('Apple', 'BID', 55, 30, None), ('Apple', 'ASK', 25, 15, None), ('Apple', 'BID', 30, 5, None)])

# o, p, t = m.get_data()

# ## Analyse données

# def draw_prices_v0(p_df):
#     # p_df columns: 'Time', 'Asset', 'Bider', 'Asker', 'Price', 'Qty'
#     fig, ax = plt.subplots()
#     for asset, df in p_df.groupby('Asset'):
#         df.plot(x='Time', y='Price', ax=ax, label=asset)
#         plt.ylabel('Price')
#     plt.show()

# def compute_prices(p_df):
#     # p_df columns: 'Time', 'Asset', 'Bider', 'Asker', 'Price', 'Qty'
#     prices = dict()
#     p_df = p_df.loc[:,['Time','Asset','Price']]
#     tmax = max(p_df.loc[:,'Time'])
#     T = range(1,tmax+1)
#     for asset, df in p_df.groupby('Asset'):
#         df = df.loc[:,['Time','Price']].set_index('Time')
#         P = []
#         last_p = None
#         for t in T:
#             try:
#                 last_p = df.loc[t]
#             except:
#                 pass
#             P.append(last_p)
#         prices[asset] = (T, P)
#     return prices

# def compute_returns(p_df):
#     prices = compute_prices(p_df)
#     returns = dict()
#     for asset in prices.keys():
#         (T,P) = prices[asset]
#         P = np.array(P)
#         R = (P[1:]-P[:-1])/P[:-1] # Returns
#         mu = np.mean(R)
#         sigma = np.sqrt(np.mean((R - mu)**2))
#         R = (R - mu)/sigma # Centred reduced returns
#         returns[asset] = (T[1:], R)
#     return returns

# def draw_prices(p_df):
#     prices = compute_prices(p_df)
#     for asset in prices.keys():
#         (T,P) = prices[asset]
#         plt.plot(T, P, '-', label=asset)
#     plt.xlabel('Time')
#     plt.ylabel('Price')
#     plt.legend(loc='best')
#     plt.show()

# def draw_returns_hist(p_df, nb_pts=50):
#     returns = compute_returns(p_df)
#     hist = dict()
#     for asset in returns.keys():
#         (T, R) = returns[asset]
#         Y, X, pat = plt.hist(R, nb_pts)
#         Y = np.array(Y)
#         R = (X[1:]+X[:-1])/2
#         hist[asset] = (R, Y*R.size/(max(R)-min(R))/np.sum(Y))
#     plt.clf()
#     for asset in hist.keys():
#         (R,D) = hist[asset]
#         plt.semilogy(R, D, 'o')
#     Y = mlab.normpdf(R, 0, 1)
#     plt.semilogy(R, Y, '-k')
#     plt.xlabel('Centred reduced returns')
#     plt.ylabel('Density')
#     plt.show()
    
#draw_prices(p)
# draw_returns_hist(p, nb_pts=100)
#draw_prices_v0(p)