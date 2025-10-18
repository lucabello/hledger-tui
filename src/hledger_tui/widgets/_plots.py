from __future__ import annotations
from typing import List, Optional

from rich.color import Color
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Static
from textual_plotext import PlotextPlot

from textual.containers import VerticalScroll
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
        return 1000

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
        self.plt.xticks(
            ticks=[i for i in range(0, int(max(self.values)), self.ticks_scale)], xside=2
        )
        # NOTE: The plot doesn't always update correctly when this function is called;
        # for some reason, calling self.on_mount() makes the bar plot update correctly.
        self.on_mount()
