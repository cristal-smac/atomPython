#!/usr/bin/python

from atom import *

m = Market(['LVMH'], trace='all except orderbooks', fix='S')
m.replay('orderFileEx1.dat')
m.print_state()