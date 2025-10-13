# hledger-view

A Textual TUI application that displays monthly expenses from an `hledger` journal file. It queries `hledger` via the CLI (JSON output) rather than parsing the file directly.

## Requirements

- Python >= 3.10
- `hledger` installed on PATH
- `LEDGER_FILE` environment variable pointing to your ledger file
- (recommended) `uv` to manage and install the project

## Install (developer / using `uv`)

```bash
# using uv (recommended)
uv sync --extra dev
uv run -- python -m hledger_view
```
