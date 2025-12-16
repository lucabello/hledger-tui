from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from typing_extensions import override

from hledger_tui.core.service import HLedger
from hledger_tui.ui.base.base_tab import BaseHLedgerTab
from hledger_tui.ui.modals.tag_pivot import ModalTagPivot
from hledger_tui.ui.widgets.hledger_balance import HLedgerBalance


class HLedgerBalanceTab(BaseHLedgerTab):
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

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        hledger = HLedger(queries=HLedger.DEFAULT_HLEDGER_QUERIES)
        super().__init__(
            hledger=hledger,
            name=name,
            id=id,
            classes=classes,
        )

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
            table_title=f"←  {self.hledger.period.pretty_value}  →",
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
        self.refresh_bindings()
