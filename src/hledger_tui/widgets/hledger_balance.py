from typing import List

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from typing_extensions import override

from hledger_tui.hledger import CategoricalBalance, HLedger
from hledger_tui.widgets._account_datatable import AccountsDataTable
from hledger_tui.widgets._plots import BarPlotScroll


class HLedgerBalance(Widget):
    BINDINGS = []
    DEFAULT_CSS = """
    HLedgerBalance {
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

        BarPlotScroll {
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
        datatable_category_name: str = "Accounts",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.datatable_category_name: str = datatable_category_name
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
