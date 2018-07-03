from data_processing import *
import matplotlib.pyplot as plt

T = []
U = []
L = []

with open('trace.dat', 'r') as file:
	for line in file:
		l = line.split(';')
		if l[0] == "LowerFundValue(New)":
			plt.axvline(int(l[2]), color="black", linestyle='--')
		if "LowerFundValue" in l[0]:
			T.append(int(l[2]))
			L.append(int(l[1]))
		elif "UpperFundValue" in l[0]:
			U.append(int(l[1]))

plt.plot(T, L, '-m')
plt.plot(T, U, '-m')

Prices = extract_prices('trace.dat')
T, P = Prices['Google']
plt.plot(T, P, '-', color='orange')

plt.show()