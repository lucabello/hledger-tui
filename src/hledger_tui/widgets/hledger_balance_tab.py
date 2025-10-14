from typing import Final, List

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widget import Widget
from typing_extensions import override

from hledger_tui.hledger import CategoricalBalance, HLedger
from hledger_tui.widgets._modal_account_balance import ModalAccountBalance
from hledger_tui.widgets._plots import BarPlotScroll
from hledger_tui.widgets._account_datatable import AccountsDataTable


class HLedgerBalance(Widget):
    BINDINGS = [
        Binding(key="d", action="cycle_depth", description="Cycle Depth"),
        Binding(key="left", action="previous_period", description="Previous Period"),
        Binding(key="right", action="next_period", description="Next Period"),
        Binding(key="t", action="cycle_period_unit", description="Cycle Period"),
        Binding(key="i", action="historical_modal", description="Overview"),
    ]
    DEFAULT_CSS = """
    HLedgerBalance {
        height: auto;
    }
    HLedgerBalance AccountsDataTable {
        width: auto;
        min-width: 0%;
        max-width: 60%;
        border: round $border;
        height: 100%;
        background: $background;
    }

    HLedgerBalance BarPlotScroll {
        width: 1fr;
        height: 100%;
        border: round $border;
        border-title-align: left;
        background: $background;
    }
    """

    # TODO: get queries from an environment variable / an --option
    # TODO: add exclusions as well (e.g., for Canonical sprints)
    DEFAULT_HLEDGER_QUERIES: Final[List[str]] = [
        "acct:expenses",
        "not:acct:financial",
        "not:acct:home:rent",
        "not:acct:home:utilities",
    ]
    _hledger: HLedger

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
        )

        self._hledger = HLedger(queries=self.DEFAULT_HLEDGER_QUERIES)
        # TODO: ⚠️ START FROM HERE ⚠️
        # Move the combo of Datatable+Barplot into its own Widget, with synced scrolling
        # Then, reuse the widget in hledger_balance (which becomes the component for the tab),
        #   and in the _model_account_balance
        raise Exception("TODO: ⚠️ START FROM HERE ⚠️")

    @override
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield AccountsDataTable()
            yield BarPlotScroll()

    def on_mount(self):
        self.update_data()
        self.query_one(AccountsDataTable).focus()

    def update_data(self) -> None:
        table = self.query_one(AccountsDataTable)
        balances: List[CategoricalBalance] = self._hledger.balance()
        table.update_data(balances=balances)
        table.border_title = f"Expenses per {self._hledger.period.singular_unit}"
        bar_plot = self.query_one(BarPlotScroll)
        bar_plot.border_title = self._hledger.period.value
        bar_plot.plot.update_data(
            # categories=[
            #     b.name.ljust(max([len(b.name) for b in balances])) for b in reversed(balances)
            # ],
            categories=[""] * len(balances),
            values=[b.balance_float for b in reversed(balances)],
        )

    def action_cycle_depth(self) -> None:
        """Cycle through account depths and refresh the widgets accordingly."""
        self._hledger.depth.increment()
        self.update_data()

    def action_previous_period(self):
        """Move the HLedgerPeriod one unit in the past and refresh."""
        self._hledger.period.previous_period()
        self.update_data()

    def action_next_period(self):
        """Move the HLedgerPeriod one unit in the future and refresh."""
        self._hledger.period.next_period()
        self.update_data()

    def action_cycle_period_unit(self):
        """Cycle through time units for the HLedgerPeriod and refresh."""
        self._hledger.period.cycle_unit()
        self.update_data()

    @work
    async def action_historical_modal(self):
        """Show historical modal."""  # TODO: improve docstring
        table = self.query_one(AccountsDataTable)
        balance_over_time: List[CategoricalBalance] = self._hledger.balance_over_time(
            account=table.selected_account
        )
        # Pretty print the categories
        max_balance_length: int = max([len(b.balance) for b in balance_over_time])
        await self.app.push_screen_wait(
            ModalAccountBalance(
                account=table.selected_account,
                hledger=self._hledger,
                # categories=[
                #     f"{b.name}{' ' * (max_balance_length - len(b.balance) + 1)}({b.balance})"
                #     for b in reversed(balance_over_time)
                # ],
            )
        )
        self.update_data()
        from textual import log

        log.error("AAAAA")
