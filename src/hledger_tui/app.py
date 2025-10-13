from textual.app import App

from hledger_tui.screens.expenses import ExpensesScreen

# from hledger_tui.screens.assets import AssetsScreen


class HLedgerViewApp(App):
    TITLE = "HLedger View"
    SUB_TITLE = "Observe your finances"
    SCREENS = {
        "expenses": ExpensesScreen,
        # "assets": AssetsScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("expenses")


if __name__ == "__main__":
    app = HLedgerViewApp()
    app.run()
