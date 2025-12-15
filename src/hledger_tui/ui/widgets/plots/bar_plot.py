"""Bar plot widget for horizontal bar charts."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Static
from typing_extensions import override

from hledger_tui.ui.widgets.plots.base_plot import BasePlot


class BarPlotScroll(Widget):
    """Scrollable container for bar plots with label."""

    DEFAULT_CSS = """
    BarPlotScroll {
        Label {
            width: 100%;
            color: $border;
            text-align: center;
            text-style: bold;
        }
        VerticalScroll {
            scrollbar-size: 0 0;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Label()
        with VerticalScroll(can_focus=False, can_focus_children=False):
            yield BarPlot()
        yield Static()

    @property
    def plot(self) -> "BarPlot":
        return self.get_child_by_type(VerticalScroll).get_child_by_type(BarPlot)

    def update_label(self, content: str) -> None:
        """Update the plot label.

        Args:
            content: New label content
        """
        label = self.query_one(Label)
        label.content = content


class BarPlot(BasePlot):
    """Horizontal bar plot widget."""

    @override
    def recreate(self) -> None:
        """Recreate the bar plot with current data."""
        self.plt.clear_data()
        if not self.values or not self.categories:
            return

        self.plt.bar(
            self.categories,
            self.values,
            orientation="horizontal",
            color=self.color.triplet,
        )

        # Dynamically adjust height based on data points
        self.styles.height = max(10, min(30, len(self.categories) + 5))
        self.plt.grid(True, True)
        self.plt.frame(False)

        # NOTE: The plot doesn't always update correctly when this function is called;
        # for some reason, calling self.on_mount() makes the plot update correctly.
        self.on_mount()
