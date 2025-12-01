from typing import List

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from typing_extensions import override

from hledger_tui.hledger import CategoricalBalance, HLedger
from hledger_tui.widgets._account_datatable import AccountsDataTable
from hledger_tui.widgets._plots import PlotPlotScroll


class HLedgerAssets(Widget):
    BINDINGS = []
    DEFAULT_CSS = """
    HLedgerAssets {
        height: auto;

        AccountsDataTable {
            width: auto;
            min-width: 20%;
            max-width: 60%;
            height: 100%;
            border: round $border;
            background: $background;
            scrollbar-size: 1 1;
            border-title-align: center;
        }

        PlotPlotScroll {
            width: 1fr;
            height: 100%;
            padding: 0 1;
            background: $background;
        }
    }
    """

    _hledger: HLedger

    def __init__(
        self,
        *,
        hledger: HLedger | None = None,
        datatable_category_name: str = "Accounts",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.datatable_category_name: str = datatable_category_name
        self._hledger = hledger  # type: ignore
        super().__init__(
            name=name,
            id=id,
            classes=classes,
        )

    @override
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield AccountsDataTable(category_name=self.datatable_category_name)
            yield PlotPlotScroll()

    def on_mount(self):
        table = self.query_one(AccountsDataTable)
        table._linked_scrollable = self.query_one(VerticalScroll)

    def update_data(
        self,
        balances: List[CategoricalBalance],
        table_title: str,
        table_subtitle: str,
        plot_label: str = "",
    ) -> None:
        """Fetch data, refresh the widgets, and return it."""
        table = self.query_one(AccountsDataTable)
        table.update_data(balances=balances)
        table.border_title = table_title
        table.border_subtitle = table_subtitle
        # Don't update the plot here - it will be updated when an account is selected
        # or when update_plot() is called explicitly

    def update_plot(self, account: str | None = None) -> None:
        """Update the plot with historical balance data for the given account."""
        if not self._hledger:
            return

        table = self.query_one(AccountsDataTable)
        selected_account = account or table.selected_account

        if not selected_account:
            return

        # Fetch historical balance over time for the selected account
        balance_over_time: List[CategoricalBalance] = self._hledger.balance_over_time(
            account=selected_account, historical=True
        )

        # Update the plot
        plot = self.query_one(PlotPlotScroll)
        if balance_over_time:
            plot.plot.update_data(
                categories=[b.name for b in balance_over_time],
                values=[b.balance_float for b in balance_over_time],
            )
            plot.update_label(
                f"{selected_account} ({self._hledger.period.value}, {self._hledger.period.subdivision})"
            )

    def on_accounts_data_table_account_selected(
        self, message: AccountsDataTable.AccountSelected
    ) -> None:
        """Handle account selection in the table."""
        self.update_plot(message.account)
