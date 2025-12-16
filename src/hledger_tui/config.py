"""Central configuration for HLedger TUI application."""

from dataclasses import dataclass, field
from typing import Final, List, Optional


@dataclass
class HLedgerConfig:
    """Central configuration for HLedger TUI."""

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
        """Load configuration from environment variables.

        Returns:
            HLedgerConfig instance with values from environment or defaults.
        """
        import os

        config = cls()

        # Override with environment variables if present
        if queries_env := os.getenv("HLEDGER_TUI_QUERIES"):
            config.default_expenses_queries = [q.strip() for q in queries_env.split(",")]

        # TODO: Make this HLEDGER_TUI_EXPENSE_QUERIES and also add HLEDGER_TUI_ASSETS_QUERIES and HLEDGER_TUI_TAG_QUERIES in order to override the other sets of default queries.

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
