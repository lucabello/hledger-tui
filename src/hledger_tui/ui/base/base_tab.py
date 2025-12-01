"""Base class for HLedger tabs with common functionality."""

from abc import abstractmethod
from typing import List, Optional

from textual import work
from textual.widget import Widget
from typing_extensions import override

from hledger_tui.core.models import CategoricalBalance
from hledger_tui.core.service import HLedger
from hledger_tui.ui.modals.account_overview import ModalAccountOverview
from hledger_tui.ui.modals.tag_overview import ModalTagOverview
from hledger_tui.ui.widgets.account_datatable import AccountsDataTable


class BaseHLedgerTab(Widget):
    """Base widget for HLedger tabs with period navigation and depth cycling."""

    def __init__(
        self,
        hledger: HLedger,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize base tab.

        Args:
            hledger: HLedger service instance
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.hledger = hledger
        self._selected_tag: Optional[str] = None
        self._balances: List[CategoricalBalance] = []

    @abstractmethod
    @work(exclusive=True, thread=True)
    async def update_data(self) -> None:
        """Update tab data - must be implemented by subclasses."""
        pass

    @override
    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Validate action availability (disables period/depth actions when tag is selected)."""
        period_actions = {
            "set_period_unit",
            "previous_period",
            "next_period",
            "cycle_depth",
        }
        if action in period_actions and self._selected_tag:
            return False
        if action == "reset_view" and not self._selected_tag:
            return False
        return True

    def action_cycle_depth(self) -> None:
        """Cycle account depth and refresh data."""
        self.hledger.cycle_depth()
        self.update_data()

    def action_previous_period(self) -> None:
        """Navigate to previous period and refresh."""
        self.hledger.period.previous_period()
        self.update_data()

    def action_next_period(self) -> None:
        """Navigate to next period and refresh."""
        self.hledger.period.next_period()
        self.update_data()

    def action_set_period_unit(self, period_unit: str) -> None:
        """Set period unit and refresh data."""
        self.hledger.period.unit = period_unit  # pyright: ignore
        self.update_data()

    def action_set_period_unit_all_time(self) -> None:
        """Set period to all time and refresh."""
        self.hledger.period.unit = None
        self.update_data()

    @work
    async def action_overview_modal(self) -> None:
        """Display account or tag overview modal with historical balance data."""
        table = self.query_one(AccountsDataTable)

        if not self._selected_tag:
            # Regular account overview
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
            # Tag overview
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
            if self.hledger.depth != depth_before_modal:
                self.update_data()
