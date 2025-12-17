# hledger-tui

A beautiful, keyboard-driven terminal UI for viewing and analyzing your [hledger](https://hledger.org/) financial data. Built with [Textual](https://textual.textualize.io/), this TUI provides an intuitive interface to explore your expenses, assets, and financial statistics.

<p align="center">
  <em>Visualize your finances without leaving the terminal</em>
</p>

## ✨ Features

### 📊 Expenses Tab

- **Categorized Expenses**: View your expenses organized by account hierarchy
- **Period Navigation**: Move through time periods using `←` and `→` arrow keys
- **Flexible Time Periods**: Switch between weeks (`w`), months (`m`), quarters, and years (`y`)
- **Account Depth Control**: Cycle through different account hierarchy levels with `d`
- **Bar Charts**: Compare expenses across accounts at a glance
- **Tag Pivot Analysis**: Group expenses by tags with `T` - perfect for project tracking
- **Account Overview**: Press `o` to see detailed balance history for any account
- **Transaction View**: Press `t` to list all transactions for an account
- **Reset View**: Return to default view with `r`

### 💰 Assets Tab

- **Asset Tracking**: Monitor balances of your assets over time
- **Historical Charts**: Interactive line charts showing asset value progression
- **Time Period Controls**: Navigate through periods or view all-time data with `a`
- **Customizable Subdivisions**: View data by day (`D`), week (`W`), month (`M`), or year (`Y`)
- **Account Depth**: Adjust hierarchy depth with `d` to see summaries or detailed breakdowns
- **Account Overview**: Press `o` for detailed balance history of selected accounts
- **Transaction Details**: View transactions for any asset with `t`

### 📈 Statistics Tab

- **Journal Insights**: Comprehensive overview of your hledger journal
- **File Information**: See which journal files are being used
- **Account Summary**: Total number of accounts and detailed listings
- **Commodity Tracking**: View all commodities used in your journal
- **Transaction Statistics**: Count of transactions and other journal metrics
- **Date Ranges**: See the span of your financial data

### ⌨️ General Features

- **Keyboard-First Design**: All features accessible via keyboard shortcuts
- **Context-Sensitive Footer**: Shows available actions based on current view
- **Real-Time Updates**: Data refreshes as you navigate

## 📋 Requirements

- **Python** >= 3.10
- **hledger** installed and available on your PATH
- **LEDGER_FILE** environment variable pointing to your hledger journal file

## 💾 Installation

```bash
pip install hledger-tui
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

That's it! Use the keyboard shortcuts shown in the footer to navigate and explore your financial data.

## �� Development

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
