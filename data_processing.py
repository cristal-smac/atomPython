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