# hledger-tui

A beautiful, keyboard-driven terminal UI for viewing and analyzing your [hledger](https://hledger.org/) financial data. Built with [Textual](https://textual.textualize.io/), this TUI provides an intuitive interface to explore your expenses, assets, and financial statistics.

<p align="center">
  <em>Observe your finances without leaving the terminal!</em>
</p>

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
