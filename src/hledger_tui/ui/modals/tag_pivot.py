from typing import List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, Label, RadioButton, RadioSet


class SimpleRadioButton(RadioButton):
    BUTTON_INNER = "x"


class ModalTagPivot(ModalScreen):
    BINDINGS = [
        Binding(key="r", action="reset", description="Reset"),
        Binding(key="q", action="close_modal", description="Close"),
        Binding(key="escape", action="close_modal", description="Close"),
    ]
    DEFAULT_CSS = """
    ModalTagPivot {
        align: center middle;
        content-align: center middle;


        Vertical {
            border: wide $border;
            width: 50%;
            height: 70%;
            padding: 1 1;
        }

        Label {
            height: 1;
            text-align: center;
            width: 1fr;
        }

        Input {
            height: 1fr;
            width: 4fr;
        }
        RadioSet{
            height: 1fr;
            width: 4fr;
        }
    }
    """
    DEFAULT_NONE_TAG: str = "(None)"

    def __init__(
        self,
        *,
        choices: List[str] = [],
        title: str = "",
        selected: Optional[str] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            id=id,
            classes=classes,
        )
        self._title: str = title
        self._choices: List[str] = choices
        self._selected: Optional[str] = selected

    def compose(self) -> ComposeResult:
        """Show historical balance for an account."""
        with Vertical():
            yield Label("Tag Pivot")
            with RadioSet(compact=True):
                for choice in self._choices:
                    yield SimpleRadioButton(
                        f"tag:{choice}", value=(f"tag:{choice}" == self._selected)
                    )
            yield Footer()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.dismiss(event.pressed.label.plain)

    def action_reset(self):
        self._selected = None
        self.dismiss(self._selected)

    def action_close_modal(self):
        """Close modal."""
        self.dismiss(self._selected)
