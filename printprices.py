from data_processing import *
import matplotlib.pyplot as plt

# ------ #
# Prices #
# ------ #

Prices = extract_prices('trace.dat')
T, P = Prices['Google']
plt.plot(T, P, '-', color='orange', label="Price")
plt.xlabel("Time")
plt.ylabel("Price")

# Fundamental value

T = []
U = []
FV = []
MFV = []
L = []

with open('trace.dat', 'r') as file:
	for line in file:
		l = line.split(';')
		if l[0] == "LowerFundValue":
			T.append(int(l[2]))
			L.append(int(l[1]))
		elif l[0] == "FundValue":
			FV.append(int(l[1]))
		elif l[0] == "UpperFundValue":
			U.append(int(l[1]))
			MFV.append((U[-1]+L[-1])//2)

plt.plot(T, U, ':k', label="Upper fund. value")
plt.plot(T, FV, '--k', label="Fund. value")
#plt.plot(T, MFV, '--k', label="Mean fund. value")
plt.plot(T, L, ':k', label="Lower fund. value")

plt.legend(loc='best')
plt.show(block=False)

# ---------- #
# Quantities #
# ---------- #

plt.figure()

T, Q = extract_qties('trace.dat')
plt.plot(T, Q, '-', color='orange')

with open('trace.dat', 'r') as file:
	for line in file:
		l = line.split(';')
		if l[0] == "Day":
			plt.axvline(int(l[3]), color="black", linestyle='--')

plt.xlabel('Tick')
plt.ylabel('Sum of quantities')
plt.show(block=False)

plt.figure()

draw_returns_hist('trace.dat', 'Google', 100)