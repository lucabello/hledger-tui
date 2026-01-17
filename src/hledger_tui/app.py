import os
import subprocess
from pathlib import Path
from typing import Optional

import typer
from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Header,
    TabbedContent,
    TabPane,
)

from hledger_tui.config import config
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
    file: Optional[str] = typer.Option(
        None,
        "-f",
        "--file",
        help="Path to your hledger journal file. Takes precedence over LEDGER_FILE environment variable.",
    ),
    serve: bool = typer.Option(
        False,
        "--serve",
        help="Run the app in web app mode, accessible via browser",
    ),
    host: str = typer.Option(
        "localhost",
        "--host",
        help="Host to bind the web server to (only used with --serve)",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        help="Port to bind the web server to (only used with --serve)",
    ),
):
    """
    A beautiful, keyboard-driven terminal UI for viewing and analyzing your hledger financial data.

    \b
    Examples:
      hledger-tui                              Run in terminal mode
      hledger-tui -f /path/to/journal.ledger   Run with specific ledger file
      hledger-tui --serve                      Run in web app mode (accessible via browser)
      hledger-tui --serve --host 0.0.0.0       Run web app mode, accessible from any network interface
      hledger-tui --serve --port 3000          Run web app mode on port 3000

    \b
    Environment Variables:
      LEDGER_FILE              Path to your hledger journal file (can be overridden with -f/--file)
      HLEDGER_TUI_DEPTH        Default depth for account hierarchy display
      HLEDGER_TUI_COMMODITY    Default commodity symbol for display

    For more information, visit: https://github.com/lucabello/hledger-tui
    """
    # Set LEDGER_FILE if --file flag is provided (takes precedence over environment variable)
    if file:
        file_path = Path(file).expanduser().resolve()
        if not file_path.exists():
            typer.echo(f"Error: Ledger file not found: {file_path}", err=True)
            raise typer.Exit(1)
        os.environ["LEDGER_FILE"] = str(file_path)
    elif config.ledger_file:
        # Use ledger_file from config if --file flag not provided
        os.environ["LEDGER_FILE"] = config.ledger_file

    # Verify LEDGER_FILE is set
    if not os.getenv("LEDGER_FILE"):
        typer.echo(
            "Error: LEDGER_FILE environment variable is not set and no file was specified with -f/--file",
            err=True,
        )
        raise typer.Exit(1)
    if serve:
        # Run in web app mode using textual serve with --command
        try:
            subprocess.run(
                [
                    "textual",
                    "serve",
                    "--command",
                    "hledger-tui",
                    "--host",
                    host,
                    "--port",
                    str(port),
                ],
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
