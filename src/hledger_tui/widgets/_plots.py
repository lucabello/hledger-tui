from __future__ import annotations

from typing import List, Optional

from rich.color import Color
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Static
from textual_plotext import PlotextPlot
from typing_extensions import override


class BarPlotScroll(Widget):
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
    def plot(self) -> BarPlot:
        return self.get_child_by_type(VerticalScroll).get_child_by_type(BarPlot)

    def update_label(self, content: str) -> None:
        label = self.query_one(Label)
        label.content = content


class PlotPlotScroll(Widget):
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
    def plot(self) -> PlotPlot:
        return self.get_child_by_type(VerticalScroll).get_child_by_type(PlotPlot)

    def update_label(self, content: str) -> None:
        label = self.query_one(Label)
        label.content = content


class BarPlot(PlotextPlot):
    categories: List[str]
    values: List[int | float]
    color_override: Optional[Color]
    color: Color

    def __init__(
        self,
        color: Optional[Color] = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.categories: List[str] = []
        self.values: List[int | float] = []
        self.color_override = color
        self.color: Color = self.color_override or Color.parse(self.app.theme_variables["primary"])

    @override
    def on_mount(self) -> None:
        super().on_mount()
        self.app.theme_changed_signal.subscribe(self, lambda _: self._update_colors())

    @property
    def ticks_scale(self) -> int:
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

    def _update_colors(self):
        """Update the plot color; this functions is used to respond to a theme_changed event."""
        self.color = self.color_override or Color.parse(self.app.theme_variables["primary"])
        if self.categories:
            self.update_data(self.categories, self.values)

    def update_data(
        self,
        categories: List[str],
        values: List[int | float],
    ):
        """Update widget data and refresh it."""
        self.categories = categories
        self.values = values
        self.recreate()

    def recreate(self):
        """Refresh the bar plot with data saved in the BarPlot instance."""
        self.plt.clear_data()
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
        if not self.values:
            return
        # Generate ticks for both positive and negative values
        min_value = min(self.values)
        max_value = max(self.values)
        ticks = []
        # Add negative ticks if there are negative values
        if min_value < 0:
            ticks.extend([i for i in range(int(min_value), 0, self.ticks_scale)])
        # Add positive ticks
        ticks.extend([i for i in range(0, int(max_value), self.ticks_scale)])
        self.plt.xticks(ticks=ticks, xside=2)
        # NOTE: The plot doesn't always update correctly when this function is called;
        # for some reason, calling self.on_mount() makes the bar plot update correctly.
        self.on_mount()


class PlotPlot(PlotextPlot):
    categories: List[str]
    values: List[int | float]
    color_override: Optional[Color]
    color: Color

    def __init__(
        self,
        color: Optional[Color] = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.categories: List[str] = []
        self.values: List[int | float] = []
        self.color_override = color
        self.color: Color = self.color_override or Color.parse(self.app.theme_variables["primary"])

    @override
    def on_mount(self) -> None:
        super().on_mount()
        self.app.theme_changed_signal.subscribe(self, lambda _: self._update_colors())

    @property
    def ticks_scale(self) -> int:
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

    def _update_colors(self):
        """Update the plot color; this functions is used to respond to a theme_changed event."""
        self.color = self.color_override or Color.parse(self.app.theme_variables["primary"])
        if self.categories:
            self.update_data(self.categories, self.values)

    def update_data(
        self,
        categories: List[str],
        values: List[int | float],
    ):
        """Update widget data and refresh it."""
        self.categories = categories
        self.values = values
        self.recreate()

    def recreate(self):
        """Refresh the plot with data saved in the PlotPlot instance."""
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
