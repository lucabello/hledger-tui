from typing import List, Optional

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from typing_extensions import override

from hledger_tui.core.models import AccountHistoricalBalance, CategoricalBalance
from hledger_tui.core.service import HLedger
from hledger_tui.ui.modals.account_overview import ModalAccountOverview
from hledger_tui.ui.modals.tag_overview import ModalTagOverview
from hledger_tui.ui.widgets.account_datatable import AccountsDataTable
from hledger_tui.ui.widgets.hledger_assets import HLedgerAssets


class HLedgerAssetsTab(Widget):
    BINDINGS = [
        ("a", "set_period_unit_all_time", "All Time"),
        ("m", "set_period_unit('months')", "Months"),
        ("y", "set_period_unit('years')", "Years"),
        Binding("D", "set_period_subdivision('daily')", "Daily"),
        Binding("W", "set_period_subdivision('weekly')", "Weekly"),
        Binding("M", "set_period_subdivision('monthly')", "Monthly"),
        Binding("Y", "set_period_subdivision('yearly')", "Yearly"),
        Binding(key="d", action="cycle_depth", description="Depth"),
        Binding(key="o", action="overview_modal", description="Overview"),
        Binding(key="left", action="previous_period", description="Previous Period", show=False),
        Binding(key="right", action="next_period", description="Next Period", show=False),
    ]
    DEFAULT_CSS = """
    HLedgerAssetsTab {
        height: auto;
    }
    """

    # TODO: get queries from an environment variable / an --option
    # TODO: add exclusions as well (e.g., for Canonical sprints)

    DEFAULT_MINIMUM_DEPTH: int = 1
    DEFAULT_MAXMIMUM_DEPTH: int = 3
    hledger: HLedger

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

        self.hledger = HLedger(queries=HLedger.DEFAULT_HLEDGER_ASSETS_QUERIES)
        self.hledger.period.unit = "years"
        self.hledger.period.subdivision = "weekly"
        self._balances: List[AccountHistoricalBalance] = []
        self._selected_tag: Optional[str] = None

    @override
    def compose(self) -> ComposeResult:
        yield HLedgerAssets(hledger=self.hledger)

    def on_mount(self):
        # Load data asynchronously after the UI is rendered
        self.call_after_refresh(self.update_data)

    @work(exclusive=True, thread=True)
    async def update_data(self) -> None:
        self._balances: List[AccountHistoricalBalance] = self.hledger.assets()
        self._account_balances: List[CategoricalBalance] = [
            CategoricalBalance(b.name, b.balances[-1].balance) for b in self._balances
        ]
        self._accounts = [b.name for b in self._balances]
        hledger_assets = self.query_one(HLedgerAssets)
        hledger_assets.update_data(
            balances=self._account_balances,
            table_title=f"←  {self.hledger.period.pretty_value}  →",
            table_subtitle=f"Depth: {self.hledger.depth}",
        )
        # Update plot for the currently selected account (if any)
        hledger_assets.update_plot()

    @override
    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""
        if action == "set_period_unit" and self._selected_tag:
            return False
        if action == "previous_period" and self._selected_tag:
            return False
        if action == "next_period" and self._selected_tag:
            return False
        if action == "cycle_depth" and self._selected_tag:
            return False
        return True

    def action_cycle_depth(self) -> None:
        """Cycle through account depths and refresh the widgets accordingly."""
        self.hledger.cycle_depth()
        self.update_data()

    def action_previous_period(self):
        """Move the HLedgerPeriod one unit in the past and refresh."""
        self.hledger.period.previous_period()
        self.update_data()

    def action_next_period(self):
        """Move the HLedgerPeriod one unit in the future and refresh."""
        self.hledger.period.next_period()
        self.update_data()

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
        self.update_plot()

    def update_plot(self) -> None:
        """Update only the plot with the selected account's balance over time."""
        hledger_assets = self.query_one(HLedgerAssets)
        hledger_assets.update_plot()

    @work
    async def action_overview_modal(self):
        """Show historical modal."""  # TODO: improve docstring
        table = self.query_one(AccountsDataTable)
        if not self._selected_tag:
            if not table.selected_account:
                return
            period_before_modal = self.hledger.period.value
            await self.app.push_screen_wait(
                ModalAccountOverview(
                    selected_account=table.selected_account,
                    accounts=[b.name for b in self._balances or []],
                    hledger=self.hledger,
                )
            )
            if self.hledger.period.value != period_before_modal:
                self.update_data()
        else:
            await self.app.push_screen_wait(
                ModalTagOverview(
                    tag=self._selected_tag,
                    tag_value=table.selected_account,
                    accounts=[b.name for b in self._balances or []],
                    hledger=self.hledger,
                )
            )
