"""Cross-platform subprocess executor for hledger-tui.

Provides a sh-like API using subprocess module for Windows compatibility.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class CommandError(Exception):
    """Exception raised when a command fails."""

    def __init__(self, command: List[str], returncode: int, stderr: Optional[str] = None):
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        message = f"Command '{' '.join(command)}' failed with exit code {returncode}"
        if stderr:
            message += f"\nStderr: {stderr}"
        super().__init__(message)


class SubprocessExecutor:
    """Cross-platform command executor using subprocess.

    Provides a convenient API similar to the sh library, but with better
    Windows support using the standard subprocess module.
    """

    def __init__(self, env: Optional[Dict[str, str]] = None):
        """Initialize the executor.

        Args:
            env: Optional environment variables to pass to subprocess
        """
        self.env = env or {}

    def _kwargs_to_args(self, kwargs: Dict[str, Any]) -> List[str]:
        """Convert keyword arguments to command-line arguments.

        This is the inverse of _parse_extra_options in service.py.
        Converts Python-style kwargs to command-line flags:

        - Boolean True: flag without value (e.g., {'cost': True} → '--cost')
        - False/None: skip the flag
        - Other values: flag with value (e.g., {'depth': 3} → '--depth 3')

        Args:
            kwargs: Dictionary of keyword arguments

        Returns:
            List of command-line argument strings

        Examples:
            {'cost': True} → ['--cost']
            {'depth': 3} → ['--depth', '3']
            {'no_total': True} → ['--no-total']
            {'_tty_out': False} → []  (underscore prefix = internal, skip)
        """
        args = []

        for key, value in kwargs.items():
            # Skip internal parameters (start with underscore)
            if key.startswith("_"):
                continue

            # Skip False and None values
            if value is False or value is None:
                continue

            # Convert underscores to dashes
            flag = key.replace("_", "-")

            # Add flag
            if flag.startswith("-"):
                args.append(flag)
            else:
                args.append(f"--{flag}")

            # Add value if it's not a boolean flag
            if value is not True:
                args.append(str(value))

        return args

    def run(
        self,
        command: Union[str, List[str]],
        *args: str,
        capture_output: bool = True,
        text: bool = True,
        check: bool = True,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess:
        """Run a command and return the result.

        Args:
            command: Command to run (string or list)
            *args: Additional positional arguments
            capture_output: Whether to capture stdout/stderr
            text: Whether to return text (str) instead of bytes
            check: If True, raise CommandError on non-zero exit
            **kwargs: Additional keyword arguments (converted to flags)

        Returns:
            CompletedProcess with stdout, stderr, returncode

        Raises:
            CommandError: If command fails and check=True
        """
        # Build command list
        if isinstance(command, str):
            cmd_list = [command]
        else:
            cmd_list = list(command)

        # Add positional arguments
        cmd_list.extend(args)

        # Add keyword arguments as flags
        cmd_list.extend(self._kwargs_to_args(kwargs))

        # Prepare environment
        process_env = None
        if self.env:
            import os

            process_env = {**os.environ, **self.env}

        # Run command
        try:
            result = subprocess.run(
                cmd_list,
                capture_output=capture_output,
                text=text,
                check=False,  # We'll check manually for better error messages
                env=process_env,
            )
        except FileNotFoundError as e:
            raise CommandError(
                cmd_list,
                -1,
                f"Command not found: {cmd_list[0]}",
            ) from e

        # Check result
        if check and result.returncode != 0:
            raise CommandError(
                cmd_list,
                result.returncode,
                result.stderr if capture_output else None,
            )

        return result

    def __call__(
        self,
        command: Union[str, List[str]],
        *args: str,
        **kwargs: Any,
    ) -> str:
        """Convenient method to run command and get stdout as string.

        Args:
            command: Command to run
            *args: Positional arguments
            **kwargs: Keyword arguments (converted to flags)

        Returns:
            stdout as string

        Raises:
            CommandError: If command fails
        """
        result = self.run(command, *args, capture_output=True, text=True, **kwargs)
        return result.stdout


class HLedgerCommand:
    """HLedger command wrapper with sh-like API."""

    def __init__(self, executor: SubprocessExecutor):
        self.executor = executor
        self._command = "hledger"

    def __getattr__(self, name: str) -> "HLedgerSubCommand":
        """Create a subcommand (e.g., hledger.balance).

        Args:
            name: Subcommand name (e.g., 'balance', 'register')

        Returns:
            HLedgerSubCommand that can be called
        """
        return HLedgerSubCommand(self._command, name, self.executor)


class HLedgerSubCommand:
    """HLedger subcommand (e.g., hledger balance).

    Provides a callable interface similar to sh.hledger.balance().
    """

    def __init__(
        self,
        parent_command: str,
        subcommand: str,
        executor: SubprocessExecutor,
    ):
        self.parent = parent_command
        self.name = subcommand
        self.executor = executor

    def __call__(
        self,
        queries: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Execute the hledger subcommand.

        Args:
            queries: Optional list of query strings
            **kwargs: Additional command-line flags

        Returns:
            Command stdout as string

        Raises:
            CommandError: If command fails
        """
        # Build command: hledger <subcommand> [query...]
        cmd = [self.parent, self.name]

        # Add queries if provided
        if queries:
            cmd.extend(queries)

        # Execute and return stdout
        return self.executor.run(cmd, **kwargs).stdout
