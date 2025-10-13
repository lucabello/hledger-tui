from typing import List, Optional

from textual.widgets import DataTable
from typing_extensions import override

from hledger_tui.hledger import AccountBalance


class AccountsDataTable(DataTable):
    def __init__(
        self,
        *,
        root_account: Optional[str] = None,
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
        self._root_account: Optional[str] = root_account
        self._balances: List[AccountBalance] = []

    @override
    def on_mount(self) -> None:
        super().on_mount()
        self.add_columns("Account", "Balance")

    def update_data(self, balances: List[AccountBalance]):
        """Update widget data and refresh it."""
        self._balances = balances
        self.recreate()

    def recreate(self):
        """Refresh the table with data saved in the AccountsDataTable instance."""
        self.clear()
        for b in self._balances:
            self.add_row(b.account, b.balance)
