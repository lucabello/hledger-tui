from hledger_tui.hledger import HLedger

# Create an HLedger instance
hledger = HLedger()

# Set the period (e.g., last month)
hledger.period.unit = "months"
hledger.period._offset = -1  # 1 month ago

# Set the subdivision (how to break down the period)
hledger.period.subdivision = "weekly"  # weekly, monthly, quarterly, yearly, or daily

print(f"Period: {hledger.period.value}")
print(f"Subdivision: {hledger.period.subdivision}")

# Get balance changes over time for a specific account (non-cumulative)
account = "assets:cash"
print(f"\nBalance changes over time for '{account}' (historical=False):")

balance_over_time = hledger.balance_over_time(account=account, historical=False)

for balance in balance_over_time:
    print(f"  {balance.name}: {balance.balance} ({balance.balance_float})")

# Get historical balance over time (cumulative)
print(f"\nHistorical balance over time for '{account}' (historical=True):")

historical_balance = hledger.balance_over_time(account=account, historical=True)

for balance in historical_balance:
    print(f"  {balance.name}: {balance.balance} ({balance.balance_float})")

# You can also change the subdivision and get different granularity
print("\n" + "=" * 50)
hledger.period.subdivision = "daily"
print("\nDaily breakdown for the same period:")
print(f"Period: {hledger.period.value}")
print(f"Subdivision: {hledger.period.subdivision}")

daily_balances = hledger.balance_over_time(account=account)
print("\nFirst 5 days:")
for balance in daily_balances[:5]:
    print(f"  {balance.name}: {balance.balance}")
print(f"\n... (showing {len(daily_balances)} total data points)")
