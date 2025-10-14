from typing import List, Optional
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Label

from hledger_tui.hledger import HLedger, CategoricalBalance
from hledger_tui.widgets._account_datatable import AccountsDataTable
from hledger_tui.widgets._plots import BarPlotScroll


class ModalAccountBalance(ModalScreen):
    BINDINGS = [
        Binding(key="t", action="cycle_period_unit", description="Cycle Period"),
        Binding(
            key="r", action="cycle_period_subdivision", description="Cycle Period Subdivision"
        ),
        Binding(key="left", action="previous_period", description="Previous Period"),
        Binding(key="right", action="next_period", description="Next Period"),
        Binding(key="q", action="close_historical_modal", description="Close"),
        Binding(key="escape", action="close_historical_modal", description="Close"),
    ]
    DEFAULT_CSS = """
    ModalAccountBalance {
        align: center middle;
    }
    ModalAccountBalance Vertical {
        align: center middle;
        width: 80%;
        height: 80%;
    }
    ModalAccountBalance Horizontal {
        align: center middle;
        border: round $border;
        border-title-align: center;
    }
    ModalAccountBalance AccountsDataTable {
        width: auto;
        min-width: 0%;
        max-width: 60%;
    }
    ModalAccountBalance BarPlotScroll {
        width: 1fr;
    }
    ModalAccountBalance BarPlotScroll BarPlot {
        align: center middle;
    }
    ModalAccountBalance Label {
        padding: 0 1;
    }
    """

    _hledger: HLedger

    def __init__(
        self,
        *,
        hledger: HLedger,
        account: str,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            id=id,
            classes=classes,
        )
        self._hledger = hledger
        self._account = account

    def compose(self) -> ComposeResult:
        """Show historical balance for an account."""
        with Vertical():
            with Horizontal():
                yield AccountsDataTable(category_name="Period")
                yield BarPlotScroll()
            yield Footer()

    def on_mount(self) -> None:
        self.update_data()

    def update_data(self) -> None:
        horizontal = self.query_one(Horizontal)
        horizontal.border_title = f"{self._account} | {self._hledger.period.value} ({self._hledger.period.subdivision} balance)"
        balance_over_time: List[CategoricalBalance] = self._hledger.balance_over_time(
            account=self._account
        )
        table = self.query_one(AccountsDataTable)
        table.update_data(balances=balance_over_time)
        bar_plot = self.query_one(BarPlotScroll)
        bar_plot.border_title = f"{self._account} ({self._hledger.period.value})"
        bar_plot.plot.update_data(
            categories=[""] * len(balance_over_time),
            values=[b.balance_float for b in reversed(balance_over_time)],
        )

    def action_close_historical_modal(self):
        """Close historical modal."""
        self._hledger.period.subdivision_offset = 0
        self.dismiss()

    def action_cycle_period_subdivision(self):
        """Cycle through period_subdivision for the HLedgerPeriod and refresh."""
        self._hledger.period.subdivision_offset += 1
        self.update_data()

    def action_previous_period(self):
        """Move the HLedgerPeriod one unit in the past and refresh."""
        self._hledger.period.previous_period()
        self.update_data()

    def action_cycle_period_unit(self):
        """Cycle through time units for the HLedgerPeriod and refresh."""
        self._hledger.period.subdivision_offset = 0
        self._hledger.period.cycle_unit()
        self.update_data()

    def action_next_period(self):
        """Move the HLedgerPeriod one unit in the future and refresh."""
        self._hledger.period.next_period()
        self.update_data()
