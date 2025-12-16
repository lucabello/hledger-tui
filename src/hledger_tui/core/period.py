"""Period management for HLedger queries."""

from datetime import datetime, timedelta
from typing import Literal


class HLedgerPeriod:
    """Represents a time period for HLedger queries with relative offset.

    Args:
        unit: Time unit ('weeks', 'months', 'quarters', 'years') or None for all time
        offset: Period offset (negative for past, positive for future, 0 for current)
    """

    unit: str | None
    _offset: int

    def __init__(
        self,
        unit: str | None = "months",
        subdivision: str = "weekly",
        offset: int = 0,
    ):
        self.unit = unit
        self.subdivision = subdivision
        self._offset = offset

        self.subdivision_offset: int = 0

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, HLedgerPeriod)
            and self.unit == other.unit
            and self._offset == other._offset
        )

    @property
    def singular_unit(self) -> str:
        """Unit in singular form (e.g., 'month' instead of 'months')."""
        if self.unit is None:
            return "all time"
        return self.unit[:-1]

    @property
    def value(self) -> str | None:
        """HLedger-compatible period string, or None for all time."""
        if self.unit is None:
            return None
        direction: Literal["ago", "ahead"] = "ago" if self._offset <= 0 else "ahead"
        # Drop the 's' from the unit if it's 1 - not necessary for HLedger, just for aesthetics
        pretty_unit = self.unit[:-1] if abs(self._offset) <= 1 else self.unit
        if self._offset == 0:
            return f"this {pretty_unit}"
        return f"{abs(self._offset)} {pretty_unit} {direction}"

    def _get_period_date(self) -> str:
        """Calculate the actual date or period string (e.g., '2025/03' or '2025/Q1')."""
        if self.unit is None:
            return "All Time"

        today = datetime.now()

        if self.unit == "weeks":
            # Calculate the start of the week (Monday)
            days_since_monday = today.weekday()
            start_of_this_week = today - timedelta(days=days_since_monday)
            # Apply offset (negative offset means past, positive means future)
            target_week_start = start_of_this_week + timedelta(weeks=self._offset)
            return target_week_start.strftime("%Y/%m/%d")

        elif self.unit == "months":
            # Calculate target month
            target_month = today.month + self._offset
            target_year = today.year

            # Handle year overflow/underflow
            while target_month > 12:
                target_month -= 12
                target_year += 1
            while target_month < 1:
                target_month += 12
                target_year -= 1

            return f"{target_year:04d}/{target_month:02d}"

        elif self.unit == "quarters":
            # Calculate target quarter
            current_quarter = (today.month - 1) // 3 + 1
            target_quarter = current_quarter + self._offset
            target_year = today.year

            # Handle year overflow/underflow
            while target_quarter > 4:
                target_quarter -= 4
                target_year += 1
            while target_quarter < 1:
                target_quarter += 4
                target_year -= 1

            return f"{target_year:04d}/Q{target_quarter}"

        elif self.unit == "years":
            target_year = today.year + self._offset
            return f"{target_year:04d}"

        return ""

    @property
    def pretty_value(self) -> str:
        """Human-readable period string with date (e.g., '1 month ago (2024/11)')."""
        if self.unit is None:
            return "All Time"

        base_value = self.value or ""
        date_info = self._get_period_date()

        if date_info:
            return f"{base_value} ({date_info})"
        return base_value

    def previous_period(self):
        """Move to the previous period (offset -= 1)."""
        self._offset -= 1

    def next_period(self):
        """Move to the next period (offset += 1)."""
        self._offset += 1
