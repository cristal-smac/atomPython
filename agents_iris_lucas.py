class Trader(object):
    trader_count = 0
    def __init__(self, market, initial_assets, cash, risk_aversion, aggressiveness, loss_tolerance, expected_earnings):
        Trader.trader_count += 1
        self.trader_id = Trader.trader_count
        self.cash = cash
        self.assets = initial_assets
        self.risk_aversion = risk_aversion
        self.aggressiveness = aggressiveness
        self.herding = 1 if risk_aversion > 50 else 0
        self.loss_tolerance = loss_tolerance
        self.expected_earnings = expected_earnings
    def __str__(self):
        return str(self.trader_id)
    def add_cash(self, n):
        self.cash += n
    def add_assets(self, n):
        self.assets += n

class MRA(Trader):
	''' Mean reversion agent'''
	def __str__(self):
		return "MRA %i" % self.trader_id
	def decide_order(self, market):
		return None
	def update(self):
		pass
	def still_valid(o):
		return True