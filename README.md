# atom
Agent-Based Financial Platform
by Philippe Mathieu & Rémi Morvan

*atom.py*: main file, atom core

*testatom.py*: a simple test file to see the basis of what atom can do

*Atom.ipynb*: A notebook to see the full range of the possibilities offered by atom

*Agents.ipynb*: A notebook introduicing agents that are more "evolved" than simple ZITs

*DeterministicArtificialTraders.ipynb*: A notebook introduicing the three different kind of
Deterministic Artificial Traders that are described in "A deterministic behaviour for realistic price dynamics
  
*OrderExecution.pdf/tex*: A short description about why it seems that there doesn't exist a total order on the set of limit orders
  that gives the permutation in which a sequence should be executed in order to maximize a given welfare
  
*OrderExecution.ipynb*: A notebook showing the code used to find counterexamples used in OrderExecution.pdf

*DrawOrderBooks.ipynb*: A notebook that generates some tikz code to draw an orderbook read in a trace file

**DrawOrderBooks.ipynb should not be run before OrderExecution.ipynb, as the latter generates a trace.dat file that is 
read by the first notebook**


*binary_heap.py*: A Python implementation of binary heaps used by atom.py

*data_processing.py*: Some functions that makes reading a trace file easier
