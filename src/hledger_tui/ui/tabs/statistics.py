from textual import work
from textual.app import ComposeResult
from textual.widget import Widget
from typing_extensions import override

from hledger_tui.core.service import HLedger
from hledger_tui.ui.widgets.hledger_statistics import HLedgerStatistics


class HLedgerStatisticsTab(Widget):
    DEFAULT_CSS = """
    HLedgerStatisticsTab {
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
        yield HLedgerStatistics()

    def on_mount(self) -> None:
        # Load data asynchronously after the UI is rendered
        self.call_after_refresh(self.update_statistics)

    @work(exclusive=True, thread=True)
    async def update_statistics(self) -> None:
        """Load and display journal statistics."""
        try:
            stats_output = HLedger.stats()
            files = HLedger.files()
            all_accounts = HLedger.all_accounts()
            commodities = HLedger.commodities()

            # Update the widget with the fetched data
            hledger_statistics = self.query_one(HLedgerStatistics)
            hledger_statistics.update_data(
                stats_output=stats_output,
                files=files,
                all_accounts=all_accounts,
                commodities=commodities,
            )
        except Exception as e:
            import traceback

            from textual.widgets import Static

            error_msg = f"[bold red]Error loading statistics:[/bold red]\n\n{str(e)}\n\n{traceback.format_exc()}"
            hledger_statistics = self.query_one(HLedgerStatistics)
            hledger_statistics.loading = False
            stats_widget = hledger_statistics.query_one("#stats-content", Static)
            stats_widget.update(error_msg)
