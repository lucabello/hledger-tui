from typing import List, Optional

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from typing_extensions import override

from hledger_tui.hledger import CategoricalBalance, HLedger
from hledger_tui.modals.account_overview import ModalAccountOverview
from hledger_tui.modals.tag_overview import ModalTagOverview
from hledger_tui.modals.tag_pivot import ModalTagPivot
from hledger_tui.widgets._account_datatable import AccountsDataTable
from hledger_tui.widgets.hledger_balance import HLedgerBalance


class HLedgerBalanceTab(Widget):
    BINDINGS = [
        ("w", "set_period_unit('weeks')", "Weeks"),
        ("m", "set_period_unit('months')", "Months"),
        ("y", "set_period_unit('years')", "Years"),
        Binding(key="d", action="cycle_depth", description="Depth"),
        Binding(key="o", action="overview_modal", description="Overview"),
        Binding(key="left", action="previous_period", description="Previous Period", show=False),
        Binding(key="right", action="next_period", description="Next Period", show=False),
        Binding("T", "tag_pivot_modal", "Tag Pivot"),
        Binding(key="r", action="reset_view", description="Reset"),
    ]
    DEFAULT_CSS = """
    HLedgerBalanceTab {
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

        self.hledger = HLedger(queries=HLedger.DEFAULT_HLEDGER_QUERIES)
        self._balances: List[CategoricalBalance] = []
        self._selected_tag: Optional[str] = None

    @override
    def compose(self) -> ComposeResult:
        yield HLedgerBalance()

    def on_mount(self):
        # Load data asynchronously after the UI is rendered
        self.call_after_refresh(self.update_data)

    @work(exclusive=True, thread=True)
    async def update_data(self) -> None:
        self._balances = self.hledger.balance()
        self._balances_accounts = [b.name for b in self._balances]
        hledger_balance = self.query_one(HLedgerBalance)
        hledger_balance._hledger = self.hledger
        hledger_balance._tag_filter = None
        hledger_balance.update_data(
            balances=self._balances,
            table_title=self.hledger.period.pretty_value,
            table_subtitle=f"Depth: {self.hledger.depth}",
        )

    @work(exclusive=True, thread=True)
    async def update_tag_data(self, tag: str) -> None:
        self._balances = self.hledger.tag_balance(tag=tag, pivot=tag)
        self._balances_accounts = [b.name for b in self._balances]
        hledger_balance = self.query_one(HLedgerBalance)
        hledger_balance._hledger = self.hledger
        # For tag pivot, the selected "account" is actually a tag value like "=value"
        # We need to set the tag filter to be "tag:key=value" format
        hledger_balance._tag_filter = tag
        hledger_balance.update_data(
            balances=self._balances,
            table_title=tag,
            table_subtitle="",
        )

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
        if action == "reset_view" and not self._selected_tag:
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
            # Save current depth and set to minimum 3 for TagOverview
            depth_before_modal = self.hledger.depth
            if self.hledger.depth < 3:
                self.hledger.depth = 3

            await self.app.push_screen_wait(
                ModalTagOverview(
                    tag=self._selected_tag,
                    tag_value=table.selected_account,
                    accounts=[b.name for b in self._balances or []],
                    hledger=self.hledger,
                )
            )

            # Restore original depth
            self.hledger.depth = depth_before_modal
            # Update data if depth changed during modal interaction
            if self.hledger.depth != depth_before_modal:
                self.update_data()

    @work
    async def action_tag_pivot_modal(self):
        """Show historical modal."""  # TODO: improve docstring
        new_selected_tag = await self.app.push_screen_wait(
            ModalTagPivot(
                title="Tag Pivot",
                choices=self.hledger.tags(),
                selected=self._selected_tag,
            )
        )
        if new_selected_tag == self._selected_tag:
            return

        self._selected_tag = new_selected_tag
        if self._selected_tag:
            self.update_tag_data(self._selected_tag)
        else:
            self.update_data()

    def action_reset_view(self) -> None:
        """Reset the view by clearing the selected tag."""
        self._selected_tag = None
        self.update_data()
