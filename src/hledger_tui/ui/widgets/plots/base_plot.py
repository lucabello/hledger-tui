"""Base plot widget with shared functionality."""

from abc import abstractmethod
from typing import List, Optional

from rich.color import Color
from textual_plotext import PlotextPlot
from typing_extensions import override


class BasePlot(PlotextPlot):
    """Base class for all plot widgets.

    Consolidates shared functionality for color management, data updates,
    and theme change handling.
    """

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
        """Initialize base plot.

        Args:
            color: Optional color override for the plot
            name: Widget name
            id: Widget ID
            classes: CSS classes
            disabled: Whether widget is disabled
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.categories: List[str] = []
        self.values: List[int | float] = []
        self.color_override = color
        self.color: Color = self.color_override or Color.parse(self.app.theme_variables["primary"])

    @override
    def on_mount(self) -> None:
        """Set up theme change subscription."""
        super().on_mount()
        self.app.theme_changed_signal.subscribe(self, lambda _: self._update_colors())

    def _update_colors(self) -> None:
        """Update plot color on theme change."""
        self.color = self.color_override or Color.parse(self.app.theme_variables["primary"])
        if self.categories:
            self.update_data(self.categories, self.values)

    def update_data(
        self,
        categories: List[str],
        values: List[int | float],
    ) -> None:
        """Update plot data.

        Args:
            categories: List of category labels
            values: List of numeric values
        """
        self.categories = categories
        self.values = values
        self.recreate()

    @abstractmethod
    def recreate(self) -> None:
        """Recreate the plot with current data.

        Must be implemented by subclasses for specific plot types.
        """
        pass
