# hledger-tui

[![PyPi Release](https://img.shields.io/pypi/v/hledger-tui?label=PyPi&color=blue)](https://pypi.org/project/hledger-tui/)
[![GitHub Release](https://img.shields.io/github/v/release/lucabello/hledger-tui?label=GitHub&color=blue)](https://github.com/lucabello/hledger-tui/releases)
[![Publish to PyPi](https://github.com/lucabello/hledger-tui/actions/workflows/publish.yaml/badge.svg)](https://github.com/lucabello/hledger-tui/actions/workflows/publish.yaml)
![Commits Since Release](https://img.shields.io/github/commits-since/lucabello/hledger-tui/latest?label=Commits%20since%20last%20release&color=darkgreen)

A beautiful, keyboard-driven terminal UI for viewing and analyzing your [hledger](https://hledger.org/) financial data. Built with [Textual](https://textual.textualize.io/), this TUI provides an intuitive interface to explore your expenses, assets, and financial statistics.

<p align="center">
  <em>Observe your finances without leaving the terminal!</em>
</p>


<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/d2e28224-c2a7-44ac-90e5-4c040863bfdb" alt="Expenses Balance" width="300"/></td>
    <td><img src="https://github.com/user-attachments/assets/de723952-dbb4-4987-adbf-b95be07071b7" alt="Tag Pivot" width="300"/></td>
    <td><img src="https://github.com/user-attachments/assets/843a833a-a721-4415-bd78-0f536683b0c8" alt="Expenses Balance by Tag" width="300"/></td>
    <td><img src="https://github.com/user-attachments/assets/843a833a-a721-4415-bd78-0f536683b0c8" alt="Overview of a tag" width="300"/></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/d257d651-1372-49fd-b6be-a9da8bcd5e03" alt="Assets Balance" width="300"/></td>
    <td><img src="https://github.com/user-attachments/assets/b5d0a0e4-c611-4082-ad35-484504df0fd3" alt="Transactions List" width="300"/></td>
    <td><img src="https://github.com/user-attachments/assets/2ee19b3b-ed77-44a2-b5d9-7ef2b74d03fe" alt="Statistics" width="300"/></td>
    <td><img src="https://github.com/user-attachments/assets/b069d7d2-0c8c-4e25-b7fc-7471723d149d" alt="Command Palette" width="300"/></td>
  </tr>
</table>


## ✨ Features

- **📊 Expenses Analysis**: Categorized expense tracking with bar charts, tag pivoting, and flexible time period navigation (weeks, months, quarters, years)
- **💰 Asset Monitoring**: Track asset balances over time with interactive line charts and customizable time subdivisions (day, week, month, year)
- **📈 Statistics Dashboard**: Comprehensive journal insights including account summaries, commodity tracking, and transaction metrics
- **🔍 Detailed Views**: Dive into account overviews, transaction lists, and balance histories for any account
- **⌨️ Keyboard-Driven**: Fast navigation with intuitive keyboard shortcuts and context-sensitive footer
- **🎨 Visual Charts**: Compare data across accounts and time periods with built-in bar and line charts

## 📋 Requirements

- **Python** >= 3.10
- **hledger** >= 1.25 installed and available on your PATH
- **LEDGER_FILE** environment variable or `-f`/`--file` flag specifying your hledger journal file

## 💾 Installation

```bash
pip install hledger-tui
```

Or try it without installing (requires [uv](https://docs.astral.sh/uv/)):

```bash
uvx hledger-tui
```

## 🎮 Usage

1. **Set up your environment** (optional if using `-f` flag):
   ```bash
   export LEDGER_FILE=/path/to/your/journal.ledger
   ```

2. **Launch the TUI**:
   ```bash
   hledger-tui
   ```
   
   Or with a specific ledger file:
   ```bash
   hledger-tui -f /path/to/your/journal.ledger
   ```
   
   Or alternatively:
   ```bash
   hledger tui
   ```

3. **Web App Mode** (optional):
   
   You can also run hledger-tui as a web application accessible via browser:
   ```bash
   hledger-tui --serve
   ```
   
   This will start a web server and provide a URL to access the TUI in your browser.

### Command-Line Options

- `-f`, `--file`: Specify the path to your hledger journal file (takes precedence over `LEDGER_FILE` environment variable)
- `--serve`: Run the app in web app mode, accessible via browser
- `--help`: Show help message with all available options and examples

That's it! Use the keyboard shortcuts shown in the footer to navigate and explore your financial data.

## ⚙️ Configuration

hledger-tui can be configured using a YAML config file or environment variables. The config file is the recommended approach for most users, while environment variables are useful for temporary overrides or containerized deployments.

When the same setting is specified in multiple places, they are applied in this priority order (highest to lowest):

1. **Environment variables** (e.g., `HLEDGER_TUI_DEPTH=3`)
2. **Config file** (`~/.config/hledger-tui/config.yaml`)
3. **Default values** (built into the application)

### Configuration File (Recommended)

Create a config file at the platform-specific location:

- **Linux**: `~/.config/hledger-tui/config.yaml`
- **macOS**: `~/Library/Application Support/hledger-tui/config.yaml`
- **Windows**: `%LOCALAPPDATA%\hledger-tui\config.yaml`

**Example config.yaml:**

```yaml
# Path to hledger file:oOptional if LEDGER_FILE is set, or when using `-f`/`--file`
ledger_file: /path/to/hledger.journal
# Query defaults for filtering results in various tabs
queries:
  assets:
    - acct:assets
  expenses:
    - acct:expenses
  tags:
    - acct:expenses

# Display settings
depth: 2
commodity: ""  # Empty = use market prices; set to "$" or "€" to convert

# Period settings
period:
  unit: months          # Options: weeks, months, quarters, years
  subdivision: weekly   # Options: daily, weekly, monthly, yearly

# Extra options for HLedger commands
extra_options:
  balance: []   # Example: ["--cost", "--depth", "4"]
  register: []  # Example: ["--related", "--cost"]
```

### Environment Variables

You can override any config file setting using environment variables. This is especially useful for CI/CD, containers, or temporary changes.

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `LEDGER_FILE` | Path to your hledger journal file (can be overridden with `-f` flag) | None | `/path/to/journal.ledger` |
| `HLEDGER_TUI_QUERIES_ASSETS` | JSON array of asset query filters | `["acct:assets", "acct:liabilities", ...]` | `'["acct:assets", "acct:liabilities"]'` |
| `HLEDGER_TUI_QUERIES_EXPENSES` | JSON array of expense query filters | `["acct:expenses", "not:acct:financial", ...]` | `'["acct:expenses", "not:tag:excluded"]'` |
| `HLEDGER_TUI_QUERIES_TAGS` | JSON array of tag query filters | `["acct:expenses"]` | `'["acct:expenses", "acct:income"]'` |
| `HLEDGER_TUI_DEPTH` | Default depth for account hierarchy display | `2` | `3` |
| `HLEDGER_TUI_COMMODITY` | Currency for exchange conversion (empty = use market prices) | `` (empty) | `€`, `$`, `USD` |
| `HLEDGER_TUI_EXTRA_OPTIONS_BALANCE` | JSON array of extra options for `hledger balance` command | `[]` | `'["--cost", "--depth", "4"]'` |
| `HLEDGER_TUI_EXTRA_OPTIONS_REGISTER` | JSON array of extra options for `hledger register` command | `[]` | `'["--cost", "--related"]'` |

**Note:** List-type environment variables must be in JSON array format. Use single quotes to wrap the JSON string in shell:

```bash
export HLEDGER_TUI_QUERIES_EXPENSES='["acct:expenses", "not:acct:financial"]'
```


### 💱 Multi-Currency Support

hledger-tui supports journals with multiple currencies, but it can only display one at a time. **Terminal plots require a single currency**, because trying to display multiple at once would make bar and line charts in the TUI cluttered, or would make lines overlap. 

There are three main strategies to handle multi-currency journals.

#### Automatic Conversion (Default)

When `HLEDGER_TUI_COMMODITY` is **not set** (default), hledger-tui uses the `--market` flag from HLedger to convert all amounts to one currency, based on market prices declared in your journal:

#### Convert to a Specific Currency

Set `HLEDGER_TUI_COMMODITY` to convert all amounts to a specific currency using the `--exchange` HLedger flag.

```bash
# Convert everything to euros
export HLEDGER_TUI_COMMODITY="€"
hledger-tui
```

The currency must exist in `hledger commodities --declared` or an error will be raised.

#### Filter Transactions by Currency

Add currency filters to your queries to view only transactions related to a specific commodity:

```bash
# Show only euro transactions
export HLEDGER_TUI_QUERIES_EXPENSES="acct:expenses,cur:€"
export HLEDGER_TUI_QUERIES_ASSETS="acct:assets,cur:€"
export HLEDGER_TUI_COMMODITY="€"
hledger-tui
```

#### Custom Conversion Options

You can pass additional HLedger options using the `HLEDGER_TUI_EXTRA_OPTIONS_BALANCE` and `HLEDGER_TUI_EXTRA_OPTIONS_REGISTER` environment variables. For example, to use cost basis conversion instead of market prices:

```bash
# Use cost basis for all balance commands
export HLEDGER_TUI_EXTRA_OPTIONS_BALANCE='["--cost"]'
export HLEDGER_TUI_EXTRA_OPTIONS_REGISTER='["--cost"]'
hledger-tui
```

These variables accept any valid HLedger command-line options and can be used to customize behavior beyond the built-in settings.

## 🔧 Development

### Prerequisites
- [uv](https://github.com/astral-sh/uv) for dependency management
- [just](https://github.com/casey/just) for running common tasks

### Setup

```bash
# Clone the repository
git clone https://github.com/lucabello/hledger-tui.git
cd hledger-tui

# Install development dependencies
uv sync --extra dev
```

### Available Commands

Run `just` to see all available commands:

```
∮ just
just --list
Available recipes:
    [build]
    build  # Build the project
    clean  # Remove build artifacts, caches, and temporary files

    [dev]
    check  # Run all quality checks
    format # Format the codebase using ruff
    lint   # Lint the codebase using ruff
    run    # Run the app with hledger-tui
    test   # Run tests
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`just check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure your code follows the project's style guidelines and includes appropriate tests.

## 📝 License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [hledger](https://hledger.org/) - Plain text accounting software
- [Textual](https://textual.textualize.io/) - Modern TUI framework for Python
- [textual-plotext](https://github.com/Textualize/textual-plotext) - Charts for Textual

## 📬 Contact

Project Link: [https://github.com/lucabello/hledger-tui](https://github.com/lucabello/hledger-tui)

---

<p align="center">
  Made with ❤️ for plain text accounting enthusiasts
</p>
