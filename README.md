# atomPython
An Agent-Based Financial Platform

[ATOM](https://github.com/cristal-smac/atom) est une plateforme de simulation de marchés financiers écrite en Java, puissante aussi bien d'un point de vue fonctionalités (multi-agents, multi-orders, multi-assets, intra and extra days, several price fixing, etc ...) que d'un point de vue rapidité.
atomPython est une version très simplifiée, écrite en Python à des fins pédagogiques. Elle ne traite notamment qu'un seul ordre (LimitOrder), ne possède qu'une fixation de prix en continu et ne permet pas de multi-day. Elle est néanmoins multi-agents et multi-assets ce qui permet de nombreuses expériences sur les marchés artificiels.

Plusieurs notebooks sont fournis afin de se familiariser avec cette plateforme

Team : P Mathieu, R Morvan, A Fleury ([CRISTAL Lab](http://www.cristal.univ-lille.fr), [SMAC team](https://www.cristal.univ-lille.fr/?rubrique27&eid=17), [Lille University](http://www.univ-lille.fr)) , O Brandouy ([Gretha](https://gretha.u-bordeaux.fr/), [Bordeaux University](https://www.u-bordeaux.fr/))

Contact : philippe.mathieu at univ-lille.fr


## Atom.ipynb
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cristal-smac/atomPython/master?filepath=Agents.ipynb)

A notebook to see the full range of the possibilities offered by this atom python version

## tp1.ipynb
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cristal-smac/atomPython/master?filepath=tp1.ipynb)

Notebook d'introduction à la manipulation de cette plateforme

## tp2.ipynb
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cristal-smac/atomPython/master?filepath=tp2.ipynb)

Notebook d'introduction à l'écriture de code avec cette plateforme


# Les fichiers disponibles

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
