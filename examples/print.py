from pprint import pprint

from hledger_tui.hledger import HLedgerApi

ledger = HLedgerApi.print()
pprint(ledger)
