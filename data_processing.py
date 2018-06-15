import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

def process_prices_per_tick(filename):
	Prices = dict()
	with open('trace.dat', 'r') as file:
		for line in file:
			l = line.split(';')
			if l[0] == "Tick" and len(l) == 4: # On ne s'intéresse qu'aux lignes de la forme Tick;Tick_number;Asset;Price
				asset = l[2]
				if asset in Prices.keys(): # Si on a déjà croisé l'asset, on ajoute le temps et le prix dans notre liste
					T, P = Prices[asset]
					T.append(int(l[1]))
					P.append(int(l[3]))
				else:
					Prices[asset] = [int(l[1])], [int(l[3])]
	return Prices

def process_prices(filename, asset):
	Prices = []
	with open(filename, 'r') as file:
		for line in file:
			l = line.split(';')
			if l[0] == "Price" and l[1] == asset: # On ne s'intéresse qu'aux lignes de la forme Price;<asset>;Bider;Asker;Prix;Qté
				Prices.append(int(l[4]))
	return Prices

def process_returns_hist(filename, asset, nb_pts):
	Prices = np.array(process_prices(filename, asset))
	Returns = (Prices[1:]-Prices[:-1])/Prices[:-1]
	Y, X, _ = plt.hist(Returns, nb_pts) # Y contient le nombre d'occurence et X les nb_pts+1 points séparant les différentes barres de l'histogramme
	plt.clf() # On ne veut pas que le plt.hist soit affiché : il est moche
	R = (X[1:]+X[:-1])/2 # R contient la liste des centres des abscisses des barres de l'histogramme
	Y = np.array(Y)
	D = Y*R.size/(max(R)-min(R))/np.sum(Y) # D contient la densité des rentabilités
	mu = np.mean(Returns)
	sigma = np.sqrt(np.mean((Returns-mu)**2))
	N = mlab.normpdf(R, mu, sigma) # Loi normale de même espérance et écart-type que les rentabilités
	return (R, D, N)