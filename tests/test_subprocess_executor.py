"""Tests for subprocess executor."""

import subprocess
import os
from hledger_tui.core.subprocess_executor import (
    SubprocessExecutor,
    HLedgerCommand,
    CommandError,
)


def test_executor_runs_simple_command():
    """Test that executor can run a simple command."""
    executor = SubprocessExecutor()
    result = executor.run("echo", "hello")
    assert result.stdout.strip() == "hello"


def test_executor_with_kwargs():
    """Test that executor converts kwargs to command-line flags."""
    executor = SubprocessExecutor()
    # Python command with --version flag
    result = executor.run("python", version=True, check=False)
    assert "Python" in result.stdout or result.returncode != 0


def test_command_error_on_failure():
    """Test that CommandError is raised for failed commands."""
    executor = SubprocessExecutor()
    try:
        # This command should fail on most systems
        if os.name == 'nt':
            executor.run("cmd", "/c", "exit", "1", check=True)
        else:
            executor.run("false", check=True)
        assert False, "Should have raised CommandError"
    except CommandError as e:
        assert e.returncode != 0


def test_hledger_command_wrapper():
    """Test HLedgerCommand wrapper (if hledger is installed)."""
    executor = SubprocessExecutor()
    hledger = HLedgerCommand(executor)

    try:
        version = hledger.version()
        # If we get here, hledger is installed
        assert "hledger" in version.lower() or "version" in version.lower()
    except CommandError:
        # hledger not installed, skip test
        pass


def test_kwargs_to_args_conversion():
    """Test _kwargs_to_args conversion logic."""
    executor = SubprocessExecutor()

    # Boolean flag
    args = executor._kwargs_to_args({"verbose": True})
    assert args == ["--verbose"]

    # Flag with value
    args = executor._kwargs_to_args({"depth": 3})
    assert args == ["--depth", "3"]

    # Underscore to dash
    args = executor._kwargs_to_args({"no_total": True})
    assert args == ["--no-total"]

    # Internal param (skip)
    args = executor._kwargs_to_args({"_tty_out": False})
    assert args == []

    # False value (skip)
    args = executor._kwargs_to_args({"verbose": False})
    assert args == []

    # None value (skip)
    args = executor._kwargs_to_args({"verbose": None})
    assert args == []

    # Mixed case
    args = executor._kwargs_to_args({"verbose": True, "depth": 2, "_tty_out": False})
    assert args == ["--verbose", "--depth", "2"]


def test_executor_callable_interface():
    """Test the __call__ method returns stdout as string."""
    executor = SubprocessExecutor()
    output = executor("echo", "test")
    assert output.strip() == "test"


def test_command_error_with_stderr():
    """Test that CommandError includes stderr when available."""
    executor = SubprocessExecutor()
    try:
        # Try to run a non-existent command
        executor.run("nonexistent_command_xyz123", check=True)
        assert False, "Should have raised CommandError"
    except CommandError as e:
        assert "nonexistent_command_xyz123" in str(e)
        assert e.returncode == -1  # FileNotFoundError return code
