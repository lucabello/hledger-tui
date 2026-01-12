"""Commodity and amount parsing utilities for multi-currency support."""

import re
from typing import NamedTuple


class ParsedAmount(NamedTuple):
    """Result of parsing an amount string."""

    numeric_value: float
    commodity: str


class CommodityParser:
    """Parser for HLedger commodity/amount strings supporting multiple formats.

    Supports various commodity styles including:
    - Symbol-first: € 1,000.00, $ 100.50
    - Symbol-last: 1,000.00 EUR, 100.50 USD
    - Various decimal separators: 1.000,00 (European), 1,000.00 (US)
    - Arbitrary spacing between digits: 1 000 000,00 (one million)
    - Multi-character symbols: EUR, GBP, Fr, ₺, €, £, ₸, دت, лв, ₽, etc.
    """

    @staticmethod
    def parse(amount_str: str) -> ParsedAmount:
        """Parse an amount string and extract numeric value and commodity.

        Args:
            amount_str: String like "€ 1,000.00", "1.000,00 EUR", "₺1.904,22", etc.

        Returns:
            ParsedAmount with numeric_value (float) and commodity (str).

        Raises:
            ValueError: If no numeric part can be extracted from the string.
        """
        amount_str = amount_str.strip()
        if not amount_str:
            raise ValueError("Empty amount string")

        # Use regex to separate numeric and non-numeric parts
        # Match patterns like: optional sign, digits/separators/spaces, optional decimal part
        numeric_pattern = r"[-+]?(?:\d[\d\s.,]*)"
        matches = list(re.finditer(numeric_pattern, amount_str))

        if not matches:
            raise ValueError(f"No numeric part found in '{amount_str}'")

        # Find the best numeric match (usually the longest continuous sequence)
        # Use the first numeric match found
        numeric_match = matches[0]
        numeric_str = numeric_match.group(0).strip()

        # Extract commodity by removing the numeric part
        before_numeric = amount_str[: numeric_match.start()].strip()
        after_numeric = amount_str[numeric_match.end() :].strip()
        commodity = (before_numeric + " " + after_numeric).strip()

        # Extract numeric value from the matched string
        numeric_value = CommodityParser._extract_numeric_value(numeric_str)

        return ParsedAmount(numeric_value=numeric_value, commodity=commodity)

    @staticmethod
    def _extract_numeric_value(numeric_str: str) -> float:
        """Extract the float value from a numeric string.

        Handles various formats:
        - Comma as decimal: 1.000,00 -> 1000.00
        - Period as decimal: 1,000.00 -> 1000.00
        - Spaces as thousand separator: 1 000 000,00 -> 1000000.00
        - Sign: +1000.00, -500.50

        Args:
            numeric_str: A string that should represent a number with possible separators.

        Returns:
            The numeric value as a float.

        Raises:
            ValueError: If the string cannot be converted to a float.
        """
        # Remove leading/trailing whitespace
        token = numeric_str.strip()

        # Remove any spaces (they're used as thousand separators)
        token_no_spaces = token.replace(" ", "")

        # Determine the decimal separator by finding the last occurrence of . or ,
        last_period = token_no_spaces.rfind(".")
        last_comma = token_no_spaces.rfind(",")

        # Normalize the number string based on separator positions
        if last_period > last_comma:
            # Period is the decimal separator; comma is thousand separator
            # Remove all commas, keep the period
            normalized = token_no_spaces.replace(",", "")
        elif last_comma > last_period:
            # Comma is the decimal separator; period is thousand separator
            # Remove all periods, replace comma with period
            normalized = token_no_spaces.replace(".", "").replace(",", ".")
        else:
            # Neither or only one type present
            if "." not in token_no_spaces and "," not in token_no_spaces:
                # No separators, just digits and sign
                normalized = token_no_spaces
            elif "." in token_no_spaces:
                # Only periods present
                if token_no_spaces.count(".") > 1:
                    # Multiple periods = thousand separators
                    normalized = token_no_spaces.replace(".", "")
                else:
                    # Single period = decimal separator
                    normalized = token_no_spaces
            else:
                # Only commas present
                if token_no_spaces.count(",") > 1:
                    # Multiple commas = thousand separators
                    normalized = token_no_spaces.replace(",", "")
                else:
                    # Single comma = decimal separator
                    normalized = token_no_spaces.replace(",", ".")

        try:
            return float(normalized)
        except ValueError as e:
            raise ValueError(f"Cannot convert '{numeric_str}' to float: {e}")
