"""Formatting utilities for display and output."""

from typing import List

from hledger_tui.config import config
from hledger_tui.core.models import Transaction


def format_transactions_rich(transactions: List[Transaction]) -> str:
    """Format transactions into a readable text format with Rich markup.

    Args:
        transactions: List of Transaction objects to format

    Returns:
        Formatted string with transactions separated by blank lines, using Rich markup for styling
    """
    lines = []

    for transaction in transactions:
        # Add transaction header: date (dim) and description (bold)
        lines.append(f"[dim]{transaction.date}[/dim] [bold]{transaction.description}[/bold]")

        # Add each posting indented
        for posting in transaction.postings:
            # Align account and amount nicely, with total dimmed
            lines.append(
                f"    {posting.account:<50} {posting.amount:>15} [dim]{posting.total:>15}[/dim]"
            )

        # Add blank line between transactions
        lines.append("")

    return "\n".join(lines)


def format_currency(value: float, commodity: str | None = None) -> str:
    """Format a float value as currency.

    Args:
        value: The numeric value to format
        commodity: Currency symbol. Defaults to config.default_commodity

    Returns:
        Formatted currency string
    """
    commodity = commodity or config.default_commodity
    return f"{commodity} {value:,.2f}"
