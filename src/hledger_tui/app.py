from rich.console import Console
from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Header,
    Label,
    TabbedContent,
    TabPane,
)

from hledger_tui.widgets.hledger_balance import HLedgerBalance

# from hledger_tui.screens.assets import AssetsScreen


class HLedgerViewApp(App):
    TITLE = "HLedger View"
    SUB_TITLE = "Observe your finances"

    def on_mount(self) -> None:
        self.theme = "dracula"

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("[1] Balance (bal)", id="tabBalance"):
                yield HLedgerBalance()
            with TabPane("[2] Balance Sheet (bs)"):
                yield Label("1")
                yield Label("1")
                yield Label("1")
        yield Footer()


if __name__ == "__main__":
    app = HLedgerViewApp()
    app.run()
