from data_processing import *

Prices = extract_prices('trace.dat')
T, P = Prices['VAASM']
plt.plot(P, '-')
plt.xlabel("Time")
plt.ylabel("Price")


# plt.figure()
# t = len(m.traders)//99
# T_ask = [[] for i in range(t)]
# T_bid = [[] for i in range(t)]
# P_ask = [[] for i in range(t)]
# P_bid = [[] for i in range(t)]
# with open('trace.dat', 'r') as file:
# 	for line in file:
# 		l = line.split(';')
# 		if l[0] == "LimitOrder":
# 			i = (int(l[2][15:])-1)//99
# 			if l[3] == "ASK":
# 				T_ask[i].append(int(l[6]))
# 				P_ask[i].append(int(l[4]))
# 			else:
# 				T_bid[i].append(int(l[6]))
# 				P_bid[i].append(int(l[4]))
# for i in range(t):
# 	plt.subplot(t, 1, i+1)
# 	plt.plot(T_ask[i], P_ask[i], 'or')
# 	plt.plot(T_bid[i], P_bid[i], 'ob')
# 	plt.grid()


plt.figure()
draw_returns_hist('trace.dat', 'VAASM', 100)

plt.figure()
acf('trace.dat', 'VAASM')

# Gamma = [100]

# plt.figure()
# gamma_min = min(Gamma)
# gamma_max = max(Gamma)
# G = list(range(gamma_min, gamma_max+1))
# D = [0]*len(G)
# for g in Gamma:
# 	D[g-gamma_min] += 1
# plt.plot(G, D, 'o')

plt.show()