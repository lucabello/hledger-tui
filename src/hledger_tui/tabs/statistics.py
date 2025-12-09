import os
import re
from datetime import datetime
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static
from typing_extensions import override

from hledger_tui.hledger import HLedger


class HLedgerStatisticsTab(Widget):
    DEFAULT_CSS = """
    HLedgerStatisticsTab {
        height: auto;
        padding: 1 2;
    }
    
    HLedgerStatisticsTab Static {
        height: auto;
    }
    """

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
        self.hledger = HLedger()

    @override
    def compose(self) -> ComposeResult:
        yield Static("Loading statistics...", id="stats-content")

    def on_mount(self) -> None:
        self.update_statistics()

    def update_statistics(self) -> None:
        """Load and display journal statistics."""
        stats_widget = self.query_one("#stats-content", Static)
        try:
            stats_widget.update("Fetching data from hledger...")
            
            stats_output = HLedger.stats()
            files = HLedger.files()
            all_accounts = HLedger.all_accounts()
            commodities = HLedger.commodities()

            # Parse the stats output
            stats_dict = self._parse_stats(stats_output)

            # Build the statistics display
            content = self._build_statistics_display(stats_dict, files, all_accounts, commodities)

            # Update the UI
            stats_widget.update(content)
        except Exception as e:
            import traceback
            error_msg = f"[bold red]Error loading statistics:[/bold red]\n\n{str(e)}\n\n{traceback.format_exc()}"
            stats_widget.update(error_msg)

    def _parse_stats(self, stats_output: str) -> dict:
        """Parse the hledger stats output into a dictionary."""
        stats = {}
        for line in stats_output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                stats[key.strip()] = value.strip()
        return stats

    def _build_statistics_display(
        self, stats: dict, files: list[str], all_accounts: list[str], commodities: list[str]
    ) -> str:
        """Build a formatted display of statistics."""
        lines = []

        # Journal Files Section
        lines.append("[bold cyan]📁 Journal Files[/bold cyan]\n")
        main_file = stats.get("Main file", "Unknown")
        lines.append(f"  [dim]Main file:[/dim] {main_file}")

        if files:
            # Get file modification time for the main file
            main_file_path = files[0] if files else None
            if main_file_path and os.path.exists(main_file_path):
                mod_time = os.path.getmtime(main_file_path)
                mod_datetime = datetime.fromtimestamp(mod_time)
                time_diff = datetime.now() - mod_datetime
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days} day{'s' if time_diff.days != 1 else ''} ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_ago = f"{hours} hour{'s' if hours != 1 else ''} ago"
                elif time_diff.seconds > 60:
                    minutes = time_diff.seconds // 60
                    time_ago = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                else:
                    time_ago = "just now"
                lines.append(f"  [dim]Last modified:[/dim] {mod_datetime.strftime('%Y-%m-%d %H:%M:%S')} ({time_ago})")
                
                # File size
                file_size = os.path.getsize(main_file_path)
                if file_size > 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"
                elif file_size > 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                else:
                    size_str = f"{file_size} bytes"
                lines.append(f"  [dim]File size:[/dim] {size_str}")

        included_files = stats.get("Included files", "0")
        lines.append(f"  [dim]Included files:[/dim] {included_files}")
        
        if len(files) > 1:
            lines.append(f"  [dim]All files:[/dim]")
            for f in files:
                lines.append(f"    • {f}")

        lines.append("")

        # Transaction Statistics Section
        lines.append("[bold cyan]📊 Transaction Statistics[/bold cyan]\n")
        lines.append(f"  [dim]Total transactions:[/dim] {stats.get('Txns', 'Unknown')}")
        lines.append(f"  [dim]Transaction span:[/dim] {stats.get('Txns span', 'Unknown')}")
        lines.append(f"  [dim]Last transaction:[/dim] {stats.get('Last txn', 'Unknown')}")
        lines.append(f"  [dim]Transactions (last 30 days):[/dim] {stats.get('Txns last 30 days', 'Unknown')}")
        lines.append(f"  [dim]Transactions (last 7 days):[/dim] {stats.get('Txns last 7 days', 'Unknown')}")

        # Parse unmarked transactions
        unmarked_count = self._count_unmarked_transactions()
        if unmarked_count is not None:
            lines.append(f"  [dim]Unmarked transactions:[/dim] {unmarked_count}")

        lines.append("")

        # Account Statistics Section
        lines.append("[bold cyan]🏦 Account Statistics[/bold cyan]\n")
        accounts_info = stats.get("Accounts", "Unknown")
        lines.append(f"  [dim]Total accounts:[/dim] {accounts_info}")
        lines.append(f"  [dim]Payees/descriptions:[/dim] {stats.get('Payees/descriptions', 'Unknown')}")
        
        # Account breakdown by type
        account_types = self._categorize_accounts(all_accounts)
        if account_types:
            lines.append(f"  [dim]Account breakdown:[/dim]")
            for account_type, count in sorted(account_types.items()):
                lines.append(f"    • {account_type}: {count}")

        lines.append("")

        # Currency/Commodity Statistics Section
        lines.append("[bold cyan]💱 Currencies & Commodities[/bold cyan]\n")
        lines.append(f"  [dim]Total commodities:[/dim] {stats.get('Commodities', 'Unknown')}")
        if commodities:
            lines.append(f"  [dim]Available commodities:[/dim] {', '.join(commodities)}")
        lines.append(f"  [dim]Market prices:[/dim] {stats.get('Market prices', 'Unknown')}")

        lines.append("")

        # Performance Statistics Section
        lines.append("[bold cyan]⚡ Performance[/bold cyan]\n")
        runtime = stats.get("Runtime stats", "Unknown")
        lines.append(f"  [dim]Runtime stats:[/dim] {runtime}")

        return "\n".join(lines)

    def _count_unmarked_transactions(self) -> int | None:
        """Count transactions without a cleared/pending status mark."""
        try:
            import sh
            # Get all transactions with their status
            # Unmarked transactions don't have ! or * status
            output = sh.hledger.print(_tty_out=False)  # pyright: ignore
            lines = output.split("\n")
            
            unmarked = 0
            for line in lines:
                # Transaction lines start with a date (YYYY-MM-DD or YYYY/MM/DD)
                if re.match(r"^\d{4}[-/]\d{2}[-/]\d{2}", line):
                    # Check if it has a status marker (! or *)
                    # Format: YYYY-MM-DD [!|*] [description]
                    # If no status marker after date, it's unmarked
                    parts = line.split(None, 2)  # Split into at most 3 parts
                    if len(parts) >= 2:
                        # If second part is not ! or *, it's unmarked
                        if parts[1] not in ["!", "*"]:
                            unmarked += 1
                    else:
                        # No description means unmarked
                        unmarked += 1
            
            return unmarked
        except Exception:
            return None

    def _categorize_accounts(self, accounts: list[str]) -> dict[str, int]:
        """Categorize accounts by their top-level category."""
        categories = {}
        for account in accounts:
            if ":" in account:
                category = account.split(":")[0]
            else:
                category = account
            categories[category] = categories.get(category, 0) + 1
        return categories
