"""Central configuration for HLedger TUI application."""

from dataclasses import dataclass, field
from typing import Final, List, Optional

from dataconfy import ConfigManager


@dataclass
class Queries:
    """Query filters for different tabs."""

    assets: List[str] = field(
        default_factory=lambda: [
            "acct:assets",
        ]
    )
    expenses: List[str] = field(
        default_factory=lambda: [
            "acct:expenses",
        ]
    )
    tags: List[str] = field(
        default_factory=lambda: [
            "acct:expenses",
        ]
    )


@dataclass
class Period:
    """Period and subdivision settings."""

    unit: Optional[str] = "months"
    subdivision: str = "weekly"


@dataclass
class ExtraOptions:
    """Extra command-line options for hledger commands."""

    balance: List[str] = field(default_factory=list)
    register: List[str] = field(default_factory=list)


@dataclass
class HLedgerConfig:
    """Configuration settings for HLedger TUI with default queries and display options."""

    ledger_file: Optional[str] = field(default=None, metadata={"env": "LEDGER_FILE"})
    queries: Queries = field(default_factory=Queries)
    depth: int = 2
    commodity: Optional[str] = None
    period: Period = field(default_factory=Period)
    extra_options: ExtraOptions = field(default_factory=ExtraOptions)

    @classmethod
    def from_env(cls) -> "HLedgerConfig":
        """Create configuration from environment variables and config file.

        Configuration priority (highest to lowest):
            1. Environment variables (e.g., HLEDGER_TUI_DEPTH)
            2. Config file (~/.config/hledger-tui/config.yaml)
            3. Default values

        Environment variables:
            HLEDGER_TUI_QUERIES_EXPENSES: JSON array of expense queries
            HLEDGER_TUI_QUERIES_TAGS: JSON array of tag queries
            HLEDGER_TUI_QUERIES_ASSETS: JSON array of asset queries
            HLEDGER_TUI_DEPTH: Default depth (integer)
            HLEDGER_TUI_COMMODITY: Currency exchange target (empty = auto-guess with --market)
            HLEDGER_TUI_PERIOD_UNIT: Default time period unit (weeks, months, quarters, years)
            HLEDGER_TUI_PERIOD_SUBDIVISION: Default subdivision for charts (daily, weekly, monthly, yearly)
            HLEDGER_TUI_EXTRA_OPTIONS_BALANCE: JSON array of extra options for balance command
            HLEDGER_TUI_EXTRA_OPTIONS_REGISTER: JSON array of extra options for register command

        Config file location:
            Linux: ~/.config/hledger-tui/config.yaml
            macOS: ~/Library/Application Support/hledger-tui/config.yaml
            Windows: %LOCALAPPDATA%\\hledger-tui\\config.yaml

        Returns:
            HLedgerConfig instance with values from environment, config file, or defaults.
        """
        # Create config manager with environment variable support enabled
        config_manager = ConfigManager(
            app_name="hledger-tui",
            use_env_vars=True,
        )

        # Load config from file with env var overrides, or use defaults if file doesn't exist
        config = config_manager.load(cls)

        return config


# Global configuration instance
config: Final[HLedgerConfig] = HLedgerConfig.from_env()
