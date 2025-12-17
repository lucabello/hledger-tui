import subprocess
import sys

import typer
from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Header,
    TabbedContent,
    TabPane,
)

from hledger_tui.ui.tabs.assets import HLedgerAssetsTab
from hledger_tui.ui.tabs.balance import HLedgerBalanceTab
from hledger_tui.ui.tabs.statistics import HLedgerStatisticsTab


class HLedgerTUIApp(App):
    TITLE = "HLedger TUI"
    SUB_TITLE = "Observe your finances"

    def on_mount(self) -> None:
        self.theme = "dracula"

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="balanceByAccount"):
            with TabPane("Expenses", id="balanceByAccount"):
                yield HLedgerBalanceTab()
            with TabPane("Assets", id="balanceByTag"):
                yield HLedgerAssetsTab()
            with TabPane("Statistics", id="statistics"):
                yield HLedgerStatisticsTab()
        yield Footer()

    def action_switch_tab(self, tab_id: str):
        """Switch to tab by ID."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = tab_id


def main(
    serve: bool = typer.Option(
        False,
        "--serve",
        help="Run the app in web app mode, accessible via browser",
    ),
):
    """
    A beautiful, keyboard-driven terminal UI for viewing and analyzing your hledger financial data.

    \b
    Examples:
      hledger-tui              Run in terminal mode
      hledger-tui --serve      Run in web app mode (accessible via browser)

    \b
    Environment Variables:
      LEDGER_FILE              Path to your hledger journal file (required)
      HLEDGER_TUI_DEPTH        Default depth for account hierarchy display
      HLEDGER_TUI_COMMODITY    Default commodity symbol for display

    For more information, visit: https://github.com/lucabello/hledger-tui
    """
    if serve:
        # Run in web app mode using textual serve with --command
        try:
            subprocess.run(
                ["textual", "serve", "--command", "hledger-tui"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            typer.echo(f"Error running textual serve: {e}", err=True)
            raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo(
                "Error: 'textual' command not found. Make sure textual-dev is installed.",
                err=True,
            )
            raise typer.Exit(1)
    else:
        # Run in terminal mode
        app = HLedgerTUIApp()
        app.run()


def cli():
    """Entry point for the CLI."""
    typer.run(main)


if __name__ == "__main__":
    cli()
