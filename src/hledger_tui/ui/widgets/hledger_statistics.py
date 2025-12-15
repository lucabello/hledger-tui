import os
import re
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Static
from typing_extensions import override


class HLedgerStatistics(Widget):
    DEFAULT_CSS = """
    HLedgerStatistics {
        height: auto;
        padding: 1 2;
    }
    
    HLedgerStatistics Horizontal {
        width: 100%;
        height: auto;
    }
    
    HLedgerStatistics Static {
        height: auto;
        width: 50%;
        padding: 0 1;
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

    @override
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            with Horizontal():
                yield Static("Loading statistics...", id="stats-left-column")
                yield Static("", id="stats-right-column")

    def on_mount(self) -> None:
        self.loading = True

    def update_data(
        self,
        stats_output: str,
        files: list[str],
        all_accounts: list[str],
        commodities: list[str],
    ) -> None:
        """Update the statistics display with the provided data."""
        self.loading = False
        left_column = self.query_one("#stats-left-column", Static)
        right_column = self.query_one("#stats-right-column", Static)

        # Parse the stats output
        stats_dict = self._parse_stats(stats_output)

        # Build the statistics display for both columns
        left_content = self._build_left_column(stats_dict, files)
        right_content = self._build_right_column(stats_dict, all_accounts)

        # Update the UI
        left_column.update(left_content)
        right_column.update(right_content)

    def _parse_stats(self, stats_output: str) -> dict:
        """Parse the hledger stats output into a dictionary."""
        stats = {}
        for line in stats_output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                stats[key.strip()] = value.strip()
        return stats

    def _build_left_column(self, stats: dict, files: list[str]) -> str:
        """Build the left column with Journal Files and Performance sections."""
        lines = []

        # Journal Files Section
        lines.append("[bold]📁 Journal Files[/bold]\n")
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
                lines.append(
                    f"  [dim]Last modified:[/dim] {mod_datetime.strftime('%Y-%m-%d %H:%M:%S')} ({time_ago})"
                )

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
            lines.append("  [dim]All files:[/dim]")
            for f in files:
                lines.append(f"    • {f}")

        lines.append("")

        # Performance Statistics Section
        lines.append("[bold]⚡ Performance[/bold]\n")
        runtime = stats.get("Runtime stats", "Unknown")
        lines.append(f"  [dim]Runtime stats:[/dim] {runtime}")

        return "\n".join(lines)

    def _build_right_column(self, stats: dict, all_accounts: list[str]) -> str:
        """Build the right column with Transaction Statistics and Account Statistics sections."""
        lines = []

        # Transaction Statistics Section
        lines.append("[bold]📊 Transaction Statistics[/bold]\n")
        lines.append(f"  [dim]Total transactions:[/dim] {stats.get('Txns', 'Unknown')}")
        lines.append(f"  [dim]Transaction span:[/dim] {stats.get('Txns span', 'Unknown')}")
        lines.append(f"  [dim]Last transaction:[/dim] {stats.get('Last txn', 'Unknown')}")
        lines.append(
            f"  [dim]Transactions (last 30 days):[/dim] {stats.get('Txns last 30 days', 'Unknown')}"
        )
        lines.append(
            f"  [dim]Transactions (last 7 days):[/dim] {stats.get('Txns last 7 days', 'Unknown')}"
        )

        # Parse unmarked transactions
        unmarked_count = self._count_unmarked_transactions()
        if unmarked_count is not None:
            lines.append(f"  [dim]Unmarked transactions:[/dim] {unmarked_count}")

        # Parse unmarked transactions (last 30 days)
        unmarked_count_30d = self._count_unmarked_transactions(days=30)
        if unmarked_count_30d is not None:
            lines.append(
                f"  [dim]Unmarked transactions (last 30 days):[/dim] {unmarked_count_30d}"
            )

        lines.append("")

        # Account Statistics Section
        lines.append("[bold]🏦 Account Statistics[/bold]\n")
        accounts_info = stats.get("Accounts", "Unknown")
        lines.append(f"  [dim]Total accounts:[/dim] {accounts_info}")
        lines.append(
            f"  [dim]Payees/descriptions:[/dim] {stats.get('Payees/descriptions', 'Unknown')}"
        )

        # Account breakdown by type
        account_types = self._categorize_accounts(all_accounts)
        if account_types:
            lines.append("  [dim]Account breakdown:[/dim]")
            for account_type, count in sorted(account_types.items()):
                lines.append(f"    • {account_type}: {count}")

        return "\n".join(lines)

    def _count_unmarked_transactions(self, days: int | None = None) -> int | None:
        """Count transactions without a cleared/pending status mark.

        Args:
            days: If specified, only count transactions from the last N days.
        """
        try:
            from datetime import datetime, timedelta

            import sh

            # Get all transactions with their status
            # Unmarked transactions don't have ! or * status
            args = []
            if days is not None:
                # Calculate the date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                args.extend(["--begin", start_date.strftime("%Y-%m-%d")])

            output = sh.hledger.print(*args, _tty_out=False)  # pyright: ignore
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
