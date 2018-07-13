from math import log, sqrt, atan, tanh, pi, sin
import numpy as np
import matplotlib.pyplot as plt

# opening_price = 3000
# fund_value = 5000
# upper = 1.3*fund_value
# lower = 0.7*fund_value

# print("risk aversion,wa,wa optimal")
# for risk_av in range(1,11):
# 	cash = (2000000*(10-risk_av))//9
# 	invest = (2000000-cash)//opening_price
# 	pt = opening_price
# 	invest_value = invest*pt
# 	wealth = invest_value + cash
# 	wa = invest_value/wealth
# 	r_low = (lower-pt)/pt
# 	r_up = (upper-pt)/pt
# 	r_mean = (r_low+r_up)/2
# 	r_var = (r_up-r_low)**2/12
# 	wa_opt = atan(r_mean/(risk_av*r_var))/pi +.5
# 	s = "ASK" if wa > wa_opt else "BID"
# 	print("%i,%.3f,%.3f,%s" % (risk_av, wa, wa_opt, s))

# x = np.linspace(-3,3,501)
# y1 = np.arctan(x)/pi+.5
# y2 = np.tanh(x)/2+.5
# plt.plot(x, y1, '-b')
# plt.plot(x, y2, '-g')
# plt.show()

# def sgn(x):
# 	if x > 0:
# 		return 1
# 	elif x < 0:
# 		return -1
# 	else:
# 		return 0

# u = 3500
# l = 5500

# epsilon = .1
# eta = .05
# Delta = []

# for p in range(2500,6501):
# 	Delta.append((p-l)*(p-u)/((u-l)/2)**2 + 1+epsilon)
# plt.plot(range(2500,6501), Delta, '-')
# plt.grid()
# plt.show(block=False)

# plt.figure()

# u = 1100
# l = 900

# P = []
# D = [[] for i in range(11)]
# for p in range(800,1201):
# 	P.append(p)
# 	Delta = (p-l)*(p-u)/((u-l)/2)**2 + 1+epsilon
# 	Delta_tilde = (Delta-epsilon)*sgn((u+l)/2-p)/8*(.5-2*eta) + .5
# 	for i in range(11):
# 		D[i].append(Delta_tilde+(5-i)/20*(8+epsilon-Delta)/8)

# for i in [0,2,4,6,8,10]:
# 	plt.plot(P, D[i], '-', label="ra=%i"%i)
# plt.grid()
# plt.legend(loc='best')
# plt.show()

u = 6500
l = 3500
RA = list(np.linspace(15,24,10))
for ra in RA:
	Waopt = []
	i = RA.index(ra)
	for pt in range(l,u+1):
		# r_mean = (u*(log(u)-1)-l*(log(l)-1))/(u-l) - log(pt)
		# r_var = (u*(log(u)-1)-l*(log(l)-1))/(u-l)
		r_mean = ((u+l)/2-pt)/pt
		r_var = (u-l)**2/(12*pt**2)
		wa_opt = (r_mean+.31)/(ra*r_var)
		Waopt.append(wa_opt)
	plt.plot(range(l,u+1), Waopt, label='ra=%.3f'%ra)
plt.legend(loc='best')
plt.xlabel('Price')
plt.ylabel('Wa opt')
plt.grid()
plt.show()