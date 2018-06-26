import numpy as np

class MinHeap():
	''' Tas min '''
	def __init__(self, fun):
		self.tree = []
		self.size = 0
		self.fun = fun # Fonction qui à x associe f(x) la valeur selon laquelle l'arbre doit être minimisé
	def __str__(self):
		return ""
	def values(self):
		return self.tree
	def insert(self, x):
		self.tree.append(x)
		i = self.size # Position initiale de x
		self.size += 1
		# Percolation vers le haut
		while i > 0 and self.fun(self.tree[(i-1)//2]) > self.fun(x):
			self.tree[(i-1)//2], self.tree[i] = self.tree[i], self.tree[(i-1)//2]
			i = (i-1)//2
	def root(self):
		return None if self.size == 0 else self.tree[0]
	def greater_than_children(self, i):
		# Retourne le plus petit des fils de i qui est strictement plus petit que i
		if 2*i+2 < self.size:
			l = [j for j in [2*i+1, 2*i+2] if self.fun(self.tree[j]) < self.fun(self.tree[i])] # Liste de fils str plus petit que le noeud
			if len(l) == 0:
				return None
			if len(l) == 1:
				return l[0]
			return 2*i+1 if self.fun(self.tree[2*i+1]) <= self.fun(self.tree[2*i+2]) else 2*i+2
		if 2*i+1 < self.size:
			return 2*i+1 if self.fun(self.tree[2*i+1]) < self.fun(self.tree[i]) else None
		else:
			return None
	def extract_root(self):
		if self.size == 0:
			raise EmptyHeap
		root = self.tree[0]
		if self.size == 1:
			self.size -= 1
			self.tree = []
		else:
			self.size -= 1
			self.tree[0] = self.tree.pop()
			# Percolation vers le bas
			i = 0
			while self.greater_than_children(i) != None:
				j = self.greater_than_children(i)
				self.tree[i], self.tree[j] = self.tree[j], self.tree[i]
				i = j
		return root

class MaxHeap(MinHeap):
	''' Tas max '''
	def __init__(self, fun):
		self.tree = []
		self.size = 0
		self.fun = lambda x: tuple(np.multiply(-1,fun(x)))