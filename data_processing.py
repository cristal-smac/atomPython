import numpy as np
import matplotlib.pyplot as plt
import scipy.stats

def extract_prices(filename):
	Prices = dict()
	with open(filename, 'r') as file:
		for line in file:
			l = line.split(';')
			if l[0] == "Price":
				if l[1] in Prices.keys():
					T, P = Prices[l[1]]
					T.append(int(l[6]))
					P.append(int(l[4]))
				else:
					Prices[l[1]] = [int(l[6])], [int(l[4])]
	return Prices

def extract_wealths(filename):
	Wealths = dict()
	with open(filename, 'r') as file:
		for line in file:
			l = line.split(';')
			if l[0] == "AgentWealth":
				if l[1] in Wealths.keys():
					T, W = Wealths[l[1]]
					T.append(int(l[3]))
					W.append(int(l[2]))
				else:
					Wealths[l[1]] = [int(l[3])], [int(l[2])]
	return Wealths

def draw_returns_hist(filename, asset, nb_pts, tau=1):
	Prices = np.array(extract_prices(filename)[asset][1])
	Returns = np.log(Prices[tau:])-np.log(Prices[:-tau])
	Y, X, _ = plt.hist(Returns, nb_pts) # Y contient le nombre d'occurence et X les nb_pts+1 points séparant les différentes barres de l'histogramme
	plt.clf() # On ne veut pas que le plt.hist soit affiché : il est moche
	R = (X[1:]+X[:-1])/2 # R contient la liste des centres des abscisses des barres de l'histogramme
	r = np.max(np.abs(R))
	R2 = np.linspace(-r, r, nb_pts*2)
	Y = np.array(Y)
	D = Y*R.size/(max(R)-min(R))/np.sum(Y) # D contient la densité des rentabilités
	mu = np.mean(Returns)
	sigma = np.sqrt(np.mean((Returns-mu)**2))
	N = scipy.stats.norm.pdf(R2, mu, sigma) # Loi normale de même espérance et écart-type que les rentabilités
	X = ((R-mu)/sigma)**4
	plt.semilogy(R, D, '-', label='Returns for tau = %i. Kurtosis = %.2f' % (tau, 3+scipy.stats.kurtosis(Returns)))
	plt.semilogy(R2, N, '--', label='Normal PDF')
	plt.xlabel('Returns')
	plt.ylabel('Density')
	plt.legend(loc='best')
	plt.title('Distribution of returns')
	r = np.max(np.abs(R))*1.05
	plt.axis([-r, r, 10**-3, max(D)*2])
	plt.grid()
	plt.show()

def smooth(lst, p):
	lst_out = []
	n = len(lst)
	for i in range(n):
		x_inf = max(0, i-p)
		x_sup = min(n, i+p+1)
		lst_out.append(sum(lst[x_inf:x_sup])/(x_sup - x_inf))
	return lst_out