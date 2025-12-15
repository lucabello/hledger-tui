"""Bar plot widget for horizontal bar charts."""

import math

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

    @property
    def ticks_scale(self) -> int:
        """Calculate appropriate tick scale based on max value."""
        if not self.values:
            return 10

        max_value = max(self.values)
        if max_value < 100:
            return 10
        if max_value < 500:
            return 50
        if max_value < 1000:
            return 100
        if max_value < 5000:
            return 500
        if max_value < 10000:
            return 1000
        if max_value < 50000:
            return 5000
        return 10000

    @override
    def recreate(self) -> None:
        """Recreate the bar plot with current data."""
        self.plt.clear_data()
        if not self.values or not self.categories:
            return

        self.plt.bar(
            self.categories,
            self.values,
            xside="upper",
            orientation="horizontal",
            color=self.color.triplet,
            width=0,
        )

        self.styles.height = len(self.categories) + 1
        self.plt.grid(vertical=True)
        self.plt.frame(False)

        # Generate ticks for both positive and negative values
        min_value = min(self.values)
        max_value = max(self.values)
        ticks = []
        # Add negative ticks if there are negative values
        if min_value < 0:
            # Calculate how many negative ticks we need (ceiling of abs(min_value) / ticks_scale)
            num_negative_ticks = math.ceil(abs(min_value) / self.ticks_scale)
            # Generate negative ticks from -num_negative_ticks * ticks_scale to 0
            ticks.extend([-i * self.ticks_scale for i in range(num_negative_ticks, 0, -1)])
        # Add positive ticks
        ticks.extend([i for i in range(0, int(max_value), self.ticks_scale)])
        self.plt.xticks(ticks=ticks, xside=2)

        # NOTE: The plot doesn't always update correctly when this function is called;
        # for some reason, calling self.on_mount() makes the plot update correctly.
        self.on_mount()
