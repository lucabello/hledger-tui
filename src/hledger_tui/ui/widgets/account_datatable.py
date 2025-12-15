from typing import List, Optional

from textual.coordinate import Coordinate
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable
from typing_extensions import override

from hledger_tui.core.models import CategoricalBalance


class AccountsDataTable(DataTable):
    class AccountSelected(Message):
        """Message emitted when an account is selected in the table."""

        def __init__(self, account: str) -> None:
            super().__init__()
            self.account = account

    def __init__(
        self,
        category_name: str = "Account",
        linked_scrollable: Optional[Widget] = None,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        disabled: bool = False,
    ):
        """Return an AccountsDataTable widget.

        Args:
            root_account: the root of the account tree to display in the table
        """
        super().__init__(
            cursor_type="row",
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._category_name: str = category_name
        self._linked_scrollable = linked_scrollable
        self._balances: List[CategoricalBalance] = []
        self._balance_over_time: List[CategoricalBalance] = []

    @override
    def on_mount(self) -> None:
        super().on_mount()
        self.add_columns(self._category_name, "Balance")

    @property
    def selected_account(self) -> str:
        coordinate = Coordinate(row=self.cursor_row, column=0)
        if self.is_valid_coordinate(coordinate):
            return self.get_cell_at(coordinate)
        return ""

    def update_data(
        self,
        balances: Optional[List[CategoricalBalance]] = None,
    ):
        """Update widget data and refresh it."""
        if balances is not None:
            self._balances = balances
        self.recreate()

    def recreate(self):
        """Refresh the table with data saved in the AccountsDataTable instance."""
        self.clear()
        for b in self._balances:
            self.add_row(b.name, b.balance)

    @override
    def watch_scroll_y(self, old_value: float, new_value: float) -> None:
        super().watch_scroll_y(old_value, new_value)
        if self._linked_scrollable:
            self._linked_scrollable.scroll_to(x=0, y=new_value)

    @override
    def watch_cursor_coordinate(
        self, old_coordinate: Coordinate, new_coordinate: Coordinate
    ) -> None:
        super().watch_cursor_coordinate(old_coordinate, new_coordinate)
        if not self._linked_scrollable:
            return

        self._linked_scrollable.scroll_to(x=0, y=float(self.scroll_offset.y))

        # Emit message when account selection changes
        if old_coordinate.row != new_coordinate.row:
            selected = self.selected_account
            if selected:
                self.post_message(self.AccountSelected(selected))
