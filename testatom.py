#-----------------------------------------
#       ATOM Minimal Market Model
#
# Auteur  : Philippe MATHIEU
# Labo    : CRISTAL, Equipe SMAC
# Date    : 16/09/2010
# contact : philippe.mathieu@univ-lille.fr
#-----------------------------------------

#!/usr/bin/python

from atom import *

m = Market()
m.add_asset(OrderBook("Apple"))
m.add_asset(OrderBook("Microsoft"))


outfilename = 'prices.dat'
outfile = open(outfilename, 'w')
outfile.write("%s\t%s\t%s\n" % ("asset", "time", "price"))
z = []
for i in range(100):
    t = ZITTrader(['Apple', 'Microsoft'])
    m.add_trader(t)
for i in range(1000):
    p = m.run_once()
    if p != []:
        for x in p:
            outfile.write("%s\t%i\t%.2f\n" % x)
outfile.close()

'''
import sys
import commands
cmd = 'R --no-save <prices.R'
failure, output = commands.getstatusoutput(cmd)
if failure:
    print("Failed")
    sys.exit(1)
'''
