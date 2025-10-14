from typing import List, Optional

from textual.binding import Binding
from textual.coordinate import Coordinate
from textual.widgets import DataTable
from typing_extensions import override

from hledger_tui.hledger import CategoricalBalance


class AccountsDataTable(DataTable):
    def __init__(
        self,
        category_name: str = "Account",
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
        self._balances: List[CategoricalBalance] = []
        self._balance_over_time: List[CategoricalBalance] = []

    @override
    def on_mount(self) -> None:
        super().on_mount()
        self.add_columns(self._category_name, "Balance")

    @property
    def selected_account(self) -> str:
        return self.get_cell_at(Coordinate(row=self.cursor_row, column=0))

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
