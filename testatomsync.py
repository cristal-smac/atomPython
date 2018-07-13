from atom_synchronous import *
import matplotlib.pyplot as plt
import random

file = open('trace.dat', 'w')
m = Market(hist_len=10, out=file)
for i in range(100):
	m.add_trader(MRA(m, risk_aversion=random.randint(1, 100), aggressiveness=random.randint(1, 100), reversion_up=1, reversion_down=-1))
for i in range(50):
	m.run_once()
file.close()

T, P, I, Trd = extract_data('trace.dat')
plt.subplot(131)
plt.plot(T, P, '-')
plt.xlabel("Tick")
plt.ylabel("Price")
plt.subplot(132)
plt.plot(T, I, '-')
plt.xlabel("Tick")
plt.ylabel("Imbalance")
plt.subplot(133)
plt.plot(T, Trd, '-')
plt.xlabel("Tick")
plt.ylabel("Number of trades")
plt.show()