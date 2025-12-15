from typing import List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from hledger_tui.core.models import Transaction
from hledger_tui.core.service import HLedger


class ModalTransactionList(ModalScreen):
    """Modal to display a list of transactions from hledger register."""

    BINDINGS = [
        Binding(key="q", action="close_modal", description="Close"),
        Binding(key="escape", action="close_modal", description="Close"),
    ]
    DEFAULT_CSS = """
    ModalTransactionList {
        align: center middle;
        
        Vertical {
            width: 90%;
            height: 80%;
            border: wide $border;
            background: $background;
        }
        
        VerticalScroll {
            width: 1fr;
            height: 1fr;
            padding: 1 2;
        }
        
        Static {
            width: 1fr;
            height: auto;
        }
    }
    """

    def __init__(
        self,
        *,
        hledger: HLedger,
        account: str,
        tag: Optional[str] = None,
        period: Optional[str] = None,
        title: Optional[str] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        """Initialize the transaction list modal.

        Args:
            hledger: HLedger instance to query transactions
            account: Account name to show transactions for
            tag: Optional tag filter in format "tag:key=value"
            period: Optional specific period to filter transactions
            title: Optional custom title for the modal border
            name: Optional name for the screen
            id: Optional id for the screen
            classes: Optional classes for the screen
        """
        super().__init__(
            name=name,
            id=id,
            classes=classes,
        )
        self.hledger = hledger
        self._account = account
        self._tag = tag
        self._period = period
        self._title = title or f"Transactions: {account}"

    def compose(self) -> ComposeResult:
        """Compose the modal with a scrollable text view."""
        with Vertical() as vertical:
            vertical.border_title = self._title
            with VerticalScroll():
                yield Static(id="transaction-content")

    def on_mount(self) -> None:
        """Load and display transaction data when the modal mounts."""
        self.update_transactions()

    def update_transactions(self) -> None:
        """Fetch and display transactions from hledger register."""
        try:
            transactions = self.hledger.register(
                account=self._account, tag=self._tag, period=self._period
            )

            content_widget = self.query_one("#transaction-content", Static)
            if transactions:
                formatted_text = self._format_transactions(transactions)
                content_widget.update(formatted_text)
            else:
                content_widget.update("No transactions found for this account.")
        except Exception as e:
            content_widget = self.query_one("#transaction-content", Static)
            content_widget.update(f"Error loading transactions: {str(e)}")

    @staticmethod
    def _format_transactions(transactions: List[Transaction]) -> str:
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

    def action_close_modal(self) -> None:
        """Close the modal."""
        self.dismiss()
