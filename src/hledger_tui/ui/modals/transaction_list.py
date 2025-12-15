from typing import List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from hledger_tui.core import HLedger, Transaction
from hledger_tui.utils import format_transactions_rich
from hledger_tui.utils import format_transactions_rich


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
                formatted_text = format_transactions_rich(transactions)
                content_widget.update(formatted_text)
            else:
                content_widget.update("No transactions found for this account.")
        except Exception as e:
            content_widget = self.query_one("#transaction-content", Static)
            content_widget.update(f"Error loading transactions: {str(e)}")

    def action_close_modal(self) -> None:
        """Close the modal."""
        self.dismiss()
