from pprint import pprint

from hledger_tui.hledger import HLedger

print("Balances:")
balances = HLedger.balance(query="assets", period="2025/08")
pprint(balances)
