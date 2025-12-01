from hledger_tui.hledger import HLedger

# Create an HLedger instance
hledger = HLedger()

print("Current Period:", hledger.period.value)
print("Current Depth:", hledger.depth)

# Get balance data
print("\nBalances:")
balances = hledger.balance()
for balance in balances:
    print(f"  {balance.name}: {balance.balance}")
