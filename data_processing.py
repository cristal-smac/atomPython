import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

def process_prices_per_tick(filename):
	Prices = dict()
	with open(filename, 'r') as file:
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
	Returns = np.log(Prices[1:])-np.log(Prices[:-1])
	# Returns = (Prices[1:]-Prices[:-1])/Prices[:-1]
	Y, X, _ = plt.hist(Returns, nb_pts) # Y contient le nombre d'occurence et X les nb_pts+1 points séparant les différentes barres de l'histogramme
	plt.clf() # On ne veut pas que le plt.hist soit affiché : il est moche
	R = (X[1:]+X[:-1])/2 # R contient la liste des centres des abscisses des barres de l'histogramme
	Y = np.array(Y)
	D = Y*R.size/(max(R)-min(R))/np.sum(Y) # D contient la densité des rentabilités
	mu = np.mean(Returns)
	sigma = np.sqrt(np.mean((Returns-mu)**2))
	N = mlab.normpdf(R, mu, sigma) # Loi normale de même espérance et écart-type que les rentabilités
	return (R, D, N)

def process_wealth(filename):
	# Cette fonction considère que si aucun prix n'a été fixé, alors le prix actuel de l'asset est de 0.
	current_tick = 0
	Traders = []
	Prices = dict()
	Wealth = dict()
	Traders_cash = dict()
	Traders_available_assets = dict()
	Traders_assets = dict() # Clés: (agent, asset)
	last_line_type = "" # Stocke le type de la dernière ligne lue
	last_line_len = 0
	with open(filename, 'r') as file:
		for line in file:
			l = line.split(';')
			if l[0] == "Tick" and len(l) == 4:
				# On stocke chaque prix fixé
				current_tick = int(l[1])
				Prices[l[2]] = int(l[3])
			elif last_line_type == "Tick" and last_line_len == 4 and l[0] != "Tick":
			# Si on a fini de lire chaque tick, et qu'il y a déjà eu des prix fixés
				for t in Traders:
					w = Traders_cash[t]
					for a in Traders_available_assets[t]:
						w += Traders_assets[t, a]*int(Prices[a])
					l_tick, l_wealth = Wealth[t]
					l_tick.append(current_tick)
					l_wealth.append(w) 
			if l[0] == "Agent":
				if l[1] not in Traders:
					Traders.append(l[1])
					Traders_available_assets[l[1]] = []
					Wealth[l[1]] = [],[]
				Traders_cash[l[1]] = int(l[2])
				if not l[3] in Traders_available_assets[l[1]]:
					Traders_available_assets[l[1]].append(l[3])
				Traders_assets[l[1], l[3]] = int(l[4])
			last_line_type = l[0]
			last_line_len = len(l)
	return Wealth

def process_social_welfare(filename, welfare_type='utilitarian'):
	''' welfare_type = "utilitarian" (default),"min", "max" or "nash"'''
	# Individual welfare = wealth - min (0, min(wealth)) + 1
	Wealth = process_wealth(filename)
	Wealth_new = dict()
	max_tick = 0
	min_wealth = 0
	for agent in Wealth.keys():
		T, W = Wealth[agent]
		if max(T) > max_tick:
			max_tick = max(T)
		if min(W) < min_wealth:
			min_wealth = min(W)
	for agent in Wealth.keys():
		T, W = Wealth[agent]
		last_wealth = 0
		W_new = []
		for t in range(1, max_tick+1):
			if t in T:
				last_wealth = W[T.index(t)]-min_wealth+1
			W_new.append(last_wealth)
		Wealth_new[agent] = W_new
	# Wealth_new est un dictionnaire dont les clés sont les agents et les valeurs sont les listes des wealths de chaque agent à chaque tick
	Tick = range(1,max_tick+1)
	Welfare = []
	for t in Tick:
		wealth = np.array([Wealth_new[agent][t-1] for agent in Wealth_new.keys()])
		if welfare_type == 'utilitarian':
			Welfare.append(np.sum(wealth))
		if welfare_type == 'min':
			Welfare.append(np.min(wealth))
		if welfare_type == 'max':
			Welfare.append(np.max(wealth))
		# if welfare_type == 'nash':
		# 	Welfare.append(np.prod(wealth))
	return Tick, Welfare

def process_all_social_welfare(filename):
	Welfare = dict()
	for welfare_type in ['utilitarian', 'min', 'max']:
		T, W = process_social_welfare(filename, welfare_type)
		Welfare[welfare_type] = W/np.max(W)
	return T, Welfare