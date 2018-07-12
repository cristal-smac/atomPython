#!/usr/bin/python

from atom import *
from data_processing import *

file = open('trace.dat', 'w')
m = Market(['LVMH'], out=file, trace=['price'])

for i in range(100):
	m.add_trader(ZITTrader(m, q_min=1, q_max=1))
for i in range(5000):
	m.run_once()

file.close()

draw_returns_hist('trace.dat', 'LVMH', 100)