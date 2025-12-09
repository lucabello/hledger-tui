from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    TabbedContent,
    TabPane,
)

from hledger_tui.tabs.assets import HLedgerAssetsTab
from hledger_tui.tabs.balance import HLedgerBalanceTab
from hledger_tui.tabs.statistics import HLedgerStatisticsTab


class HLedgerViewApp(App):
    TITLE = "HLedger View"
    SUB_TITLE = "Observe your finances"

    # BINDINGS = [
    #     Binding(key="1", action="switch_tab('balanceTab')", show=False),
    #     Binding(key="2", action="switch_tab('balanceSheetTab')", show=False),
    # ]

    def on_mount(self) -> None:
        self.theme = "dracula"

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="balanceByAccount"):
            with TabPane("Expenses", id="balanceByAccount"):
                yield HLedgerBalanceTab()
            with TabPane("Assets", id="balanceByTag"):
                yield HLedgerAssetsTab()
                # yield Label()
                # yield HLedgerBalanceTab()
            with TabPane("Statistics", id="statistics"):
                yield HLedgerStatisticsTab()
        yield Footer()

    def action_switch_tab(self, tab_id: str):
        """Switch to the tab with the specified id."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = tab_id


if __name__ == "__main__":
    app = HLedgerViewApp()
    app.run()
