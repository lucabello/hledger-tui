from pprint import pprint

from hledger_tui.hledger import HLedger

ledger = HLedger.print()
pprint(ledger)
