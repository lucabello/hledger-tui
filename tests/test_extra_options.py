#!/usr/bin/env python3
"""Quick test script to verify extra options functionality."""

from hledger_tui.config import HLedgerConfig
from hledger_tui.core.service import HLedger


def test_config_parsing(monkeypatch):
    """Test that config parses extra options correctly."""
    # Set environment variables using monkeypatch
    monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", '["--cost", "--depth", "5"]')
    monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_REGISTER", '["--related", "--cost"]')

    # Create a fresh config instance from environment
    config = HLedgerConfig.from_env()

    print("Testing config parsing...")
    print(f"  extra_balance_options: {config.extra_options.balance}")
    print(f"  extra_register_options: {config.extra_options.register}")

    assert config.extra_options.balance == ["--cost", "--depth", "5"], (
        f"Expected ['--cost', '--depth', '5'], got {config.extra_options.balance}"
    )
    assert config.extra_options.register == ["--related", "--cost"], (
        f"Expected ['--related', '--cost'], got {config.extra_options.register}"
    )
    print("✓ Config parsing works correctly")


def test_parse_extra_options():
    """Test the _parse_extra_options method."""
    print("\nTesting _parse_extra_options method...")

    # Test boolean flags
    result = HLedger._parse_extra_options(["--cost", "--no-total"])
    assert result == {"cost": True, "no_total": True}, f"Got {result}"
    print("✓ Boolean flags parsed correctly")

    # Test key-value pairs with space
    result = HLedger._parse_extra_options(["--depth", "3", "--exchange", "USD"])
    assert result == {"depth": "3", "exchange": "USD"}, f"Got {result}"
    print("✓ Key-value pairs with space parsed correctly")

    # Test key-value pairs with equals sign
    result = HLedger._parse_extra_options(["--depth=5", "--exchange=EUR"])
    assert result == {"depth": "5", "exchange": "EUR"}, f"Got {result}"
    print("✓ Key-value pairs with = parsed correctly")

    # Test mixed boolean and key-value with space
    result = HLedger._parse_extra_options(["--cost", "--depth", "4"])
    assert result == {"cost": True, "depth": "4"}, f"Got {result}"
    print("✓ Mixed options with space parsed correctly")

    # Test mixed boolean and key-value with equals
    result = HLedger._parse_extra_options(["--cost", "--depth=5"])
    assert result == {"cost": True, "depth": "5"}, f"Got {result}"
    print("✓ Mixed options with = parsed correctly")

    # Test all three formats together: ["--cost", "--depth", "5"]
    result = HLedger._parse_extra_options(["--cost", "--depth", "5"])
    assert result == {"cost": True, "depth": "5"}, f"Got {result}"
    print("✓ Format 1: ['--cost', '--depth', '5'] parsed correctly")

    # Test format 2: ["--cost", "--depth 5"] (single string with space)
    result = HLedger._parse_extra_options(["--cost", "--depth 5"])
    assert result == {"cost": True, "depth": "5"}, f"Got {result}"
    print("✓ Format 2: ['--cost', '--depth 5'] parsed correctly")

    # Test format 3: ["--cost", "--depth=5"]
    result = HLedger._parse_extra_options(["--cost", "--depth=5"])
    assert result == {"cost": True, "depth": "5"}, f"Got {result}"
    print("✓ Format 3: ['--cost', '--depth=5'] parsed correctly")

    # Test complex scenario with multiple formats
    result = HLedger._parse_extra_options(
        ["--cost", "--depth", "3", "--exchange=USD", "--no-total"]
    )
    assert result == {"cost": True, "depth": "3", "exchange": "USD", "no_total": True}, (
        f"Got {result}"
    )
    print("✓ Complex mixed format parsed correctly")

    # Test single string with space and value
    result = HLedger._parse_extra_options(["--period 2024-01"])
    assert result == {"period": "2024-01"}, f"Got {result}"
    print("✓ Single string with space and value parsed correctly")

    # Test empty
    result = HLedger._parse_extra_options([])
    assert result == {}, f"Got {result}"
    print("✓ Empty list handled correctly")

    # Test single dash options
    result = HLedger._parse_extra_options(["-V", "-b", "2024-01-01"])
    assert result == {"V": True, "b": "2024-01-01"}, f"Got {result}"
    print("✓ Single dash options parsed correctly")
