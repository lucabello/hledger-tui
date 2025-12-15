"""Line plot widget for time series data."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Static
from typing_extensions import override

from hledger_tui.ui.widgets.plots.base_plot import BasePlot


class PlotPlotScroll(Widget):
    """Scrollable container for line plots with label."""

    DEFAULT_CSS = """
    PlotPlotScroll {
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
            yield PlotPlot()
        yield Static()

    @property
    def plot(self) -> "PlotPlot":
        return self.get_child_by_type(VerticalScroll).get_child_by_type(PlotPlot)

    def update_label(self, content: str) -> None:
        """Update the plot label.

        Args:
            content: New label content
        """
        label = self.query_one(Label)
        label.content = content


class PlotPlot(BasePlot):
    """Line plot widget for time series visualization."""

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
        """Recreate the line plot with current data."""
        self.plt.clear_data()
        if not self.values or not self.categories:
            return

        # Use numeric indices instead of date strings to avoid date parsing issues
        x_values = list(range(len(self.categories)))
        self.plt.plot(
            x_values,
            self.values,
            color=self.color.triplet,
        )

        # Dynamically adjust height based on data points for better visibility
        self.styles.height = max(10, min(30, len(self.categories) // 2 + 5))
        self.plt.grid(True, True)
        self.plt.frame(False)

        # Set x-axis ticks to show dates at regular intervals
        if len(self.categories) > 10:
            # Show only a subset of dates to avoid clutter
            step = len(self.categories) // 8
            tick_indices = [float(i) for i in range(0, len(self.categories), step)]
            tick_labels = [self.categories[int(i)] for i in tick_indices]
            self.plt.xticks(tick_indices, tick_labels)
        else:
            self.plt.xticks([float(i) for i in range(len(self.categories))], self.categories)

        # NOTE: The plot doesn't always update correctly when this function is called;
        # for some reason, calling self.on_mount() makes the plot update correctly.
        self.on_mount()
