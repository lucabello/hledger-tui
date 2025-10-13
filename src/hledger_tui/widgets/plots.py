from typing import List

from rich.color import Color
from textual_plotext import PlotextPlot
from typing_extensions import override


class BarPlot(PlotextPlot):
    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._ticks_scale: int = 100
        self._color: Color = Color.parse(self.app.theme_variables["primary"])
        self._categories: List[str] = []
        self._values: List[int | float] = []

    @override
    def on_mount(self) -> None:
        super().on_mount()
        self.app.theme_changed_signal.subscribe(self, lambda _: self._update_colors())

    def _update_colors(self):
        """Update the plot color; this functions is used to respond to a theme_changed event."""
        self._color = Color.parse(self.app.theme_variables["primary"])
        if self._categories:
            self.update_data(self._categories, self._values, self._ticks_scale)

    def update_data(
        self,
        categories: List[str],
        values: List[int | float],
        ticks_scale: int = 100,
    ):
        """Update widget data and refresh it."""
        self._categories = categories
        self._values = values
        self._ticks_scale = ticks_scale
        self.recreate()

    def recreate(self):
        """Refresh the bar plot with data saved in the BarPlot instance."""
        self.plt.clear_data()
        if not self._categories:
            return
        self.plt.bar(
            self._categories,
            self._values,
            orientation="horizontal",
            color=self._color.triplet,
            width=0,
        )
        self.styles.height = len(self._categories) + 3
        self.plt.grid(vertical=True)
        if not self._values:
            return
        self.plt.xticks(ticks=[i for i in range(0, int(max(self._values)), self._ticks_scale)])
