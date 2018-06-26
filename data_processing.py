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

def process_returns_hist(filename, asset, nb_pts):
	Prices = np.array(extract_prices(filename)[asset][1])
	Returns = np.log(Prices[1:])-np.log(Prices[:-1])
	# Returns = (Prices[1:]-Prices[:-1])/Prices[:-1]
	Y, X, _ = plt.hist(Returns, nb_pts) # Y contient le nombre d'occurence et X les nb_pts+1 points séparant les différentes barres de l'histogramme
	plt.clf() # On ne veut pas que le plt.hist soit affiché : il est moche
	R = (X[1:]+X[:-1])/2 # R contient la liste des centres des abscisses des barres de l'histogramme
	Y = np.array(Y)
	D = Y*R.size/(max(R)-min(R))/np.sum(Y) # D contient la densité des rentabilités
	mu = np.mean(Returns)
	sigma = np.sqrt(np.mean((Returns-mu)**2))
	N = scipy.stats.norm.pdf(R, mu, sigma) # Loi normale de même espérance et écart-type que les rentabilités
	return (R, D, N)