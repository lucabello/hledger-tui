"""Base class for modal screens."""

from typing import Optional

from textual.binding import Binding
from textual.screen import ModalScreen

from hledger_tui.core.service import HLedger


class BaseModal(ModalScreen):
    """Base modal screen with standard close bindings and HLedger instance."""

    BINDINGS = [
        Binding(key="q", action="close_modal", description="Close"),
        Binding(key="escape", action="close_modal", description="Close"),
    ]

    def __init__(
        self,
        hledger: HLedger,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        """Initialize base modal.

        Args:
            hledger: HLedger service instance
            name: Screen name
            id: Screen ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.hledger = hledger

    def action_close_modal(self) -> None:
        """Dismiss the modal screen."""
        self.dismiss()
