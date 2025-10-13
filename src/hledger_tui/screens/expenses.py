from typing import List

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header
from typing_extensions import override

from hledger_tui.hledger import CyclicCounter, HLedgerApi, HLedgerPeriod
from hledger_tui.widgets.account_table import AccountsDataTable
from hledger_tui.widgets.plots import BarPlot


class ExpensesScreen(Screen):
    BINDINGS = [
        Binding("d", "cycle_depth()", "Depth"),
        Binding("left", "set_period_before()", "Previous Period"),
        Binding("right", "set_period_after()", "Next Period"),
        Binding("t", "cycle_time_period_unit()", "Time Unit"),
    ]
    DEFAULT_CSS = """
    ExpensesScreen AccountsDataTable {
        width: auto;
        min-width: 40%;
        border: round $border;
        height: 100%;
    }

    ExpensesScreen VerticalScroll {
        width: 1fr;
        height: 100%;
        border: round $border;
        border-title-align: left;
        background: $surface;
    }
    """

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
        self._root_account = "acct:expenses"
        # TODO: get these from an environment variable / an --option
        self._hledger_exclusions: List[str] = [
            "not:acct:financial",
            "not:acct:home:rent",
            "not:acct:home:utilities",
            # TODO: add exclusion of canonical sprints
        ]
        self._hledger_queries: List[str] = [
            self._root_account,
            *self._hledger_exclusions,
        ]
        self._account_depth: CyclicCounter = HLedgerApi.account_depth(
            account_query=self._root_account
        )
        # Minimum depth is 2 because we're showing only 1 top-level account
        self._account_depth.min = 2
        self._time_period: HLedgerPeriod = HLedgerPeriod()

    @override
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            AccountsDataTable(root_account=self._root_account),
            VerticalScroll(BarPlot(), can_focus=False, can_focus_children=False),
        )
        yield Footer()

    def on_mount(self):
        self.update_data()

    def update_data(self) -> None:
        balances = HLedgerApi.balance(
            queries=self._hledger_queries,
            depth=self._account_depth.value,
            period=self._time_period,
        )
        table = self.get_child_by_type(Horizontal).get_child_by_type(AccountsDataTable)
        table.update_data(balances=balances)
        table.border_title = f"Expenses per {self._time_period.unit.value[:-1]}"
        vertical_scroll = self.get_child_by_type(Horizontal).get_child_by_type(VerticalScroll)
        vertical_scroll.border_title = self._time_period.to_string()
        plot = vertical_scroll.get_child_by_type(BarPlot)
        plot.update_data(
            categories=[
                b.account.ljust(max([len(b.account) for b in balances]))
                for b in reversed(balances)
            ],
            values=[b.balance_float for b in reversed(balances)],
        )

    def action_cycle_depth(self) -> None:
        """Cycle through account depths and refresh the widgets accordingly."""
        self._account_depth.increment()
        self.update_data()

    def action_set_period_before(self):
        """Move the HLedgerPeriod one unit in the past and refresh."""
        self._time_period.before()
        self.update_data()

    def action_set_period_after(self):
        """Move the HLedgerPeriod one unit in the future and refresh."""
        self._time_period.after()
        self.update_data()

    def action_cycle_time_period_unit(self):
        """Cycle through time units for the HLedgerPeriod and refresh."""
        self._time_period.unit.next()
        self.update_data()
