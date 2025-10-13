from pprint import pprint

from hledger_tui.hledger import HLedgerApi

print("Balances:")
balances = HLedgerApi.balance(query="assets", period="2025/08")
pprint(balances)
