#!/usr/bin/env python3
"""Quick test script to verify extra options functionality."""

from hledger_tui.config import HLedgerConfig
from hledger_tui.core.service import HLedger


def test_config_parsing(monkeypatch):
    """Test that config parses extra options correctly."""
    # Set environment variables using monkeypatch
    monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", "--cost --depth 5")
    monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_REGISTER", "--related --cost")

    # Create a fresh config instance from environment
    config = HLedgerConfig.from_env()

    print("Testing config parsing...")
    print(f"  extra_balance_options: {config.extra_balance_options}")
    print(f"  extra_register_options: {config.extra_register_options}")

    assert config.extra_balance_options == ["--cost", "--depth", "5"], (
        f"Expected ['--cost', '--depth', '5'], got {config.extra_balance_options}"
    )
    assert config.extra_register_options == ["--related", "--cost"], (
        f"Expected ['--related', '--cost'], got {config.extra_register_options}"
    )
    print("✓ Config parsing works correctly")


def test_parse_extra_options():
    """Test the _parse_extra_options method."""
    print("\nTesting _parse_extra_options method...")

    # Test boolean flags
    result = HLedger._parse_extra_options(["--cost", "--no-total"])
    assert result == {"cost": True, "no_total": True}, f"Got {result}"
    print("✓ Boolean flags parsed correctly")

    # Test key-value pairs
    result = HLedger._parse_extra_options(["--depth", "3", "--exchange", "USD"])
    assert result == {"depth": "3", "exchange": "USD"}, f"Got {result}"
    print("✓ Key-value pairs parsed correctly")

    # Test mixed
    result = HLedger._parse_extra_options(["--cost", "--depth", "4"])
    assert result == {"cost": True, "depth": "4"}, f"Got {result}"
    print("✓ Mixed options parsed correctly")

    # Test empty
    result = HLedger._parse_extra_options([])
    assert result == {}, f"Got {result}"
    print("✓ Empty list handled correctly")
