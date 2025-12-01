"""Central configuration for HLedger TUI application."""

from dataclasses import dataclass, field
from typing import Final, List, Optional


@dataclass
class HLedgerConfig:
    """Configuration settings for HLedger TUI with default queries and display options."""

    # Query defaults
    default_expenses_queries: List[str] = field(
        default_factory=lambda: [
            "acct:expenses",
            "not:acct:financial",
            "not:acct:home:rent",
            "not:acct:home:utilities",
        ]
    )

    default_tag_queries: List[str] = field(
        default_factory=lambda: [
            "acct:expenses",
        ]
    )

    default_assets_queries: List[str] = field(
        default_factory=lambda: [
            "acct:assets",
            "acct:liabilities",
            "acct:budget",
        ]
    )

    # Display defaults
    default_depth: int = 2
    default_depth_min: int = 1
    default_depth_max: int = 4
    default_commodity: str = "€"

    # Period defaults
    default_period_unit: Optional[str] = "months"
    default_subdivision: str = "weekly"

    @classmethod
    def from_env(cls) -> "HLedgerConfig":
        """Create configuration from environment variables, falling back to defaults.

        Environment variables:
            HLEDGER_TUI_EXPENSE_QUERIES: Comma-separated expense queries
            HLEDGER_TUI_TAG_QUERIES: Comma-separated tag queries
            HLEDGER_TUI_ASSETS_QUERIES: Comma-separated asset queries
            HLEDGER_TUI_DEPTH: Default depth (integer)
            HLEDGER_TUI_COMMODITY: Default commodity symbol

        Returns:
            HLedgerConfig instance with values from environment or defaults.
        """
        import os

        config = cls()

        # Override with environment variables if present
        if expenses_queries_env := os.getenv("HLEDGER_TUI_EXPENSE_QUERIES"):
            config.default_expenses_queries = [q.strip() for q in expenses_queries_env.split(",")]

        if tag_queries_env := os.getenv("HLEDGER_TUI_TAG_QUERIES"):
            config.default_tag_queries = [q.strip() for q in tag_queries_env.split(",")]

        if assets_queries_env := os.getenv("HLEDGER_TUI_ASSETS_QUERIES"):
            config.default_assets_queries = [q.strip() for q in assets_queries_env.split(",")]

        if depth_env := os.getenv("HLEDGER_TUI_DEPTH"):
            try:
                config.default_depth = int(depth_env)
            except ValueError:
                pass

        if commodity_env := os.getenv("HLEDGER_TUI_COMMODITY"):
            config.default_commodity = commodity_env

        return config


# Global configuration instance
config: Final[HLedgerConfig] = HLedgerConfig.from_env()
