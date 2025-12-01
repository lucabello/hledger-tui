from typing import List, Optional

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer

from hledger_tui.core.models import CategoricalBalance
from hledger_tui.core.service import HLedger
from hledger_tui.ui.widgets.hledger_balance import HLedgerBalance


class ModalTagOverview(ModalScreen):
    BINDINGS = [
        Binding("d", "cycle_depth", "Depth"),
        Binding("shift+down", "change_account(1)", "Next Account"),
        Binding("shift+up", "change_account(-1)", "Previous Account"),
        Binding(key="t", action="show_transactions", description="Transactions", priority=True),
        Binding(key="q", action="close_modal", description="Close"),
        Binding(key="escape", action="close_modal", description="Close"),
    ]
    DEFAULT_CSS = """
    ModalTagOverview {
        align: center middle;
        Vertical {
            width: 60%;
            height: 80%;
        }
        Horizontal {
            border: wide $border;
            padding: 1 1;
        }
    }
    """

    hledger: HLedger

    def __init__(
        self,
        *,
        hledger: HLedger,
        tag: str,
        tag_value: str,
        accounts: List[str],
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            id=id,
            classes=classes,
        )
        self.hledger = hledger
        self._tag = tag
        self._tag_value = tag_value
        self._accounts = accounts

    def compose(self) -> ComposeResult:
        """Show historical balance for an account."""
        with Vertical():
            yield HLedgerBalance(datatable_category_name="Period")
            yield Footer()

    def on_mount(self) -> None:
        self.update_data()

    def update_data(self) -> None:
        balance_over_time: List[CategoricalBalance] = self.hledger.tag_balance(
            tag=f"{self._tag}={self._tag_value[1:]}"
        )
        hledger_balance = self.query_one(HLedgerBalance)
        hledger_balance.update_data(
            balances=balance_over_time,
            table_title="",
            table_subtitle=f"Depth: {self.hledger.depth}",
            plot_label=f"{self._tag} = {self._tag_value[1:]}",
        )

    def action_close_modal(self):
        """Close modal."""
        self.dismiss()

    def action_change_account(self, offset: int):
        selected_index: int = self._accounts.index(self._tag_value)
        new_index: int = (selected_index + offset) % len(self._accounts)
        self._tag_value = self._accounts[new_index]
        self.update_data()

    def action_cycle_depth(self) -> None:
        """Cycle through account depths and refresh the widgets accordingly."""
        self.hledger.cycle_depth()
        self.update_data()

    @work
    async def action_show_transactions(self) -> None:
        """Show transactions for the selected account with the tag filter."""
        from hledger_tui.ui.modals.transaction_list import ModalTransactionList
        from hledger_tui.ui.widgets.account_datatable import AccountsDataTable

        table = self.query_one(AccountsDataTable)
        selected_account = table.selected_account

        if not selected_account:
            return

        # Build the tag filter string
        # self._tag already contains "tag:key", so we just need to add "=value"
        # Strip the leading "=" or ":" from tag_value if present
        tag_value = self._tag_value
        if tag_value.startswith("=") or tag_value.startswith(":"):
            tag_value = tag_value[1:]
        tag_filter = f"{self._tag}={tag_value}"

        await self.app.push_screen(
            ModalTransactionList(
                hledger=self.hledger,
                account=selected_account,
                tag=tag_filter,
                period="",  # Tag view targets the whole journal, not a specific period
                title=f"Transactions: {selected_account} ({tag_filter})",
            )
        )
