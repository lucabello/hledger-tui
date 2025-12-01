from pprint import pprint

from hledger_tui.hledger import HLedger

# Create an HLedger instance with default queries
hledger = HLedger()

# Or specify custom queries
# hledger = HLedger(queries=["assets", "liabilities"])

print("Account Balances:")
balances = hledger.balance()
pprint(balances)

print("\nAssets with Historical Data:")
assets = hledger.assets()
for asset in assets:
    print(f"\n{asset.name}:")
    print(f"  Latest balance: {asset.balances[-1].balance}")
    print(f"  Number of periods: {len(asset.balances)}")
