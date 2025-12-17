"""Allow running hledger-tui as a module: python -m hledger_tui."""

from hledger_tui.app import cli

if __name__ == "__main__":
    cli()
