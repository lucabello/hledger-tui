from typing import List, Optional

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from typing_extensions import override

from hledger_tui.core.models import CategoricalBalance
from hledger_tui.core.service import HLedger
from hledger_tui.ui.widgets.account_datatable import AccountsDataTable
from hledger_tui.ui.widgets.plots.bar_plot import BarPlotScroll


class HLedgerBalance(Widget):
    BINDINGS = [
        Binding(
            key="t",
            action="show_transactions",
            description="Transactions",
            show=True,
            priority=True,
        ),
    ]
    DEFAULT_CSS = """
    HLedgerBalance {
        height: auto;

        AccountsDataTable {
            width: auto;
            min-width: 40;
            max-width: 60%;
            height: 100%;
            border: round $border;
            background: $background;
            scrollbar-size: 1 1;
            border-title-align: center;
        }

        BarPlotScroll {
            width: 1fr;
            height: 100%;
            padding: 0 1;
            background: $background;
        }
    }
    """

    _hledger: HLedger
    _tag_filter: Optional[str] = None

    def __init__(
        self,
        *,
        datatable_category_name: str = "Accounts",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.datatable_category_name: str = datatable_category_name
        self._tag_filter = None
        super().__init__(
            name=name,
            id=id,
            classes=classes,
        )

    @override
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield AccountsDataTable(category_name=self.datatable_category_name)
            yield BarPlotScroll()

    def on_mount(self):
        self.loading = True
        table = self.query_one(AccountsDataTable)
        table._linked_scrollable = self.query_one(VerticalScroll)
        self.query_one(AccountsDataTable).focus()

    def update_data(
        self,
        balances: List[CategoricalBalance],
        table_title: str,
        table_subtitle: str,
        plot_label: str = "",
    ) -> None:
        """Fetch data, refresh the widgets, and return it."""
        self.loading = False
        table = self.query_one(AccountsDataTable)
        table.update_data(balances=balances)
        table.border_title = table_title
        table.border_subtitle = table_subtitle
        bar_plot = self.query_one(BarPlotScroll)
        bar_plot.plot.update_data(
            categories=[""] * len(balances),
            values=[b.balance_float for b in reversed(balances)],
        )
        bar_plot.update_label(plot_label)

    @work
    async def action_show_transactions(self) -> None:
        """Show transactions for the selected account."""
        from hledger_tui.ui.modals.transaction_list import ModalTransactionList

        table = self.query_one(AccountsDataTable)
        selected_account = table.selected_account

        if not selected_account:
            return

        # Get hledger instance from parent context
        # This will be populated by parent widgets/tabs
        if not hasattr(self, "_hledger") or not self._hledger:
            return

        # Check if this is a tag pivot view
        if self._tag_filter:
            # In tag pivot, selected_account is like "=value" or ":value"
            # We need to use the queries from hledger and add the tag filter
            tag_value = selected_account
            if selected_account.startswith("=") or selected_account.startswith(":"):
                tag_value = selected_account[1:]
            tag_full = f"{self._tag_filter}={tag_value}"
            # Use a general account query from the hledger queries
            account_query = self._hledger.queries[0] if self._hledger.queries else "acct:expenses"

            await self.app.push_screen(
                ModalTransactionList(
                    hledger=self._hledger,
                    account=account_query,
                    tag=tag_full,
                    period="",  # Tag pivot targets the whole journal, not a specific period
                    title=f"Transactions: {tag_full}",
                )
            )
        else:
            # Normal account view - use the current period
            await self.app.push_screen(
                ModalTransactionList(
                    hledger=self._hledger,
                    account=selected_account,
                    tag=None,
                    title=f"Transactions: {selected_account}",
                )
            )
