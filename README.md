# hledger-tui

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
- **hledger** installed and available on your PATH
- **LEDGER_FILE** environment variable pointing to your hledger journal file

## 💾 Installation

```bash
pip install hledger-tui
```

Or try it without installing (requires [uv](https://docs.astral.sh/uv/)):

```bash
uvx hledger-tui
```

## 🎮 Usage

1. **Set up your environment**:
   ```bash
   export LEDGER_FILE=/path/to/your/journal.ledger
   ```

2. **Launch the TUI**:
   ```bash
   hledger-tui
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

- `--help`: Show help message with all available options and examples
- `--serve`: Run the app in web app mode, accessible via browser

That's it! Use the keyboard shortcuts shown in the footer to navigate and explore your financial data.

## ⚙️ Configuration

You can customize hledger-tui behavior using environment variables. All configuration options are optional and fall back to sensible defaults.

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `LEDGER_FILE` | **Required**. Path to your hledger journal file | None | `/path/to/journal.ledger` |
| `HLEDGER_TUI_EXPENSE_QUERIES` | Comma-separated queries for expense filtering | `acct:expenses, not:acct:financial, not:acct:home:rent, not:acct:home:utilities` | `acct:expenses, not:tag:excluded` |
| `HLEDGER_TUI_TAG_QUERIES` | Comma-separated queries for tag filtering | `acct:expenses` | `acct:expenses, acct:income` |
| `HLEDGER_TUI_ASSETS_QUERIES` | Comma-separated queries for asset filtering | `acct:assets, acct:liabilities, acct:budget` | `acct:assets, acct:liabilities` |
| `HLEDGER_TUI_DEPTH` | Default depth for account hierarchy display | `2` | `3` |
| `HLEDGER_TUI_COMMODITY` | Default commodity symbol for display | `€` | `$` |

### Example Configuration

```bash
# Basic setup with required variable
export LEDGER_FILE=/path/to/journal.ledger

# Customize expense tracking
export HLEDGER_TUI_EXPENSE_QUERIES="acct:expenses, not:acct:mortgage"

# Change default display settings
export HLEDGER_TUI_DEPTH=3
export HLEDGER_TUI_COMMODITY="$"

# Run the app
hledger-tui
```

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
