from atom_synchronous import *

m = Market()
t = MRA(m, initial_assets=10, cash=10000, risk_aversion=0.4, aggressiveness=0.7, loss_tolerance=50, expected_earnings=50)
m.add_trader(t)
m.run_once()