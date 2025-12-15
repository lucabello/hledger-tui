from typing import List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen

from hledger_tui.hledger import CategoricalBalance, HLedger
from hledger_tui.widgets.grid_footer import GridFooter
from hledger_tui.widgets.hledger_balance import HLedgerBalance


class ModalAccountOverview(ModalScreen):
    BINDINGS = [
        Binding(
            key="left",
            action="previous_period",
            description="Previous Period",
            priority=True,
            show=False,
        ),
        Binding(
            key="right",
            action="next_period",
            description="Next Period",
            priority=True,
            show=False,
        ),
        Binding("a", "set_period_unit_all_time", "All Time", priority=True),
        Binding("w", "set_period_unit('weeks')", "Weeks", priority=True),
        Binding("m", "set_period_unit('months')", "Months", priority=True),
        Binding("y", "set_period_unit('years')", "Years", priority=True),
        Binding("W", "set_period_subdivision('weekly')", "Weekly", priority=True),
        Binding("M", "set_period_subdivision('monthly')", "Monthly", priority=True),
        Binding("Y", "set_period_subdivision('yearly')", "Yearly", priority=True),
        Binding("shift+down", "change_account(1)", "Next Account"),
        Binding("shift+up", "change_account(-1)", "Previous Account"),
        Binding(key="q", action="close_historical_modal", description="Close"),
        Binding(key="escape", action="close_historical_modal", description="Close"),
    ]
    DEFAULT_CSS = """
    ModalAccountOverview {
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
        selected_account: str,
        accounts: List[str],
        use_pretty_period: bool = True,
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
        self._selected_account = selected_account
        self._accounts = accounts
        self._use_pretty_period = use_pretty_period

    def compose(self) -> ComposeResult:
        """Show historical balance for an account."""
        with Vertical():
            yield HLedgerBalance(datatable_category_name="Period")
            yield GridFooter()

    def on_mount(self) -> None:
        self.update_data()

    def update_data(self) -> None:
        balance_over_time: List[CategoricalBalance] = self.hledger.balance_over_time(
            account=self._selected_account
        )
        period_display = (
            self.hledger.period.pretty_value
            if self._use_pretty_period
            else self.hledger.period.value
        )
        hledger_balance = self.query_one(HLedgerBalance)
        hledger_balance.update_data(
            balances=balance_over_time,
            table_title=f"{self.hledger.period.subdivision} balance".title(),
            table_subtitle="",
            plot_label=f"{self._selected_account} ({period_display})",
        )

    def action_close_historical_modal(self):
        """Close historical modal."""
        self.hledger.period.subdivision_offset = 0
        self.dismiss()

    def action_set_period_unit(self, period_unit: str):
        """Set the unit for the HLedgerPeriod and refresh."""
        self.hledger.period.unit = period_unit  # pyright: ignore
        self.update_data()

    def action_set_period_unit_all_time(self):
        """Set the period to all time and refresh."""
        self.hledger.period.unit = None
        self.update_data()

    def action_set_period_subdivision(self, period_subdivision: str):
        """Set the subdivision for the HLedgerPeriod and refresh."""
        self.hledger.period.subdivision = period_subdivision
        self.update_data()

    def action_previous_period(self):
        """Move the HLedgerPeriod one unit in the past and refresh."""
        self.hledger.period.previous_period()
        self.update_data()

    def action_next_period(self):
        """Move the HLedgerPeriod one unit in the future and refresh."""
        self.hledger.period.next_period()
        self.update_data()

    def action_change_account(self, offset: int):
        selected_index: int = self._accounts.index(self._selected_account)
        new_index: int = (selected_index + offset) % len(self._accounts)
        self._selected_account = self._accounts[new_index]
        self.update_data()
