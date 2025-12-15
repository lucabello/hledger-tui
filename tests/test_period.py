"""Tests for HLedgerPeriod functionality."""

import pytest
from datetime import datetime

from hledger_tui.core.period import HLedgerPeriod


class TestHLedgerPeriodValue:
    """Test HLedgerPeriod value generation."""

    def test_default_period(self):
        """Test default period initialization."""
        period = HLedgerPeriod()
        assert period.unit == "months"
        assert period.subdivision == "weekly"
        assert period._offset == 0
        assert period.value == "this month"

    def test_all_time_period(self):
        """Test all-time period (no unit)."""
        period = HLedgerPeriod(unit=None)
        assert period.value is None
        assert period.pretty_value == "All Time"
        assert period.singular_unit == "all time"

    def test_weeks_period(self):
        """Test weekly periods."""
        period = HLedgerPeriod(unit="weeks")
        assert period.value == "this week"

        period.previous_period()
        assert period.value == "1 week ago"

        period.previous_period()
        assert period.value == "2 weeks ago"

    def test_months_period(self):
        """Test monthly periods."""
        period = HLedgerPeriod(unit="months")
        period.previous_period()
        assert period.value == "1 month ago"

        period.previous_period()
        assert period.value == "2 months ago"

    def test_years_period(self):
        """Test yearly periods."""
        period = HLedgerPeriod(unit="years")
        period.next_period()
        assert period.value == "1 year ahead"

        period.next_period()
        assert period.value == "2 years ahead"

    def test_quarters_period(self):
        """Test quarterly periods."""
        period = HLedgerPeriod(unit="quarters")
        assert period.value == "this quarter"


class TestHLedgerPeriodNavigation:
    """Test period navigation."""

    def test_previous_period(self):
        """Test moving to previous period."""
        period = HLedgerPeriod(unit="months")
        assert period._offset == 0

        period.previous_period()
        assert period._offset == -1

        period.previous_period()
        assert period._offset == -2

    def test_next_period(self):
        """Test moving to next period."""
        period = HLedgerPeriod(unit="months")
        assert period._offset == 0

        period.next_period()
        assert period._offset == 1

        period.next_period()
        assert period._offset == 2

    def test_navigation_roundtrip(self):
        """Test navigating back and forth."""
        period = HLedgerPeriod(unit="months")
        original_value = period.value

        period.next_period()
        period.next_period()
        period.previous_period()
        period.previous_period()

        assert period._offset == 0
        assert period.value == original_value


class TestHLedgerPeriodDateCalculation:
    """Test period date calculation."""

    def test_weeks_date_calculation(self):
        """Test week date calculation."""
        period = HLedgerPeriod(unit="weeks", offset=0)
        pretty = period.pretty_value
        # Should contain a date in YYYY/MM/DD format
        assert "(" in pretty and ")" in pretty
        assert "/" in pretty

    def test_months_date_calculation(self):
        """Test month date calculation."""
        period = HLedgerPeriod(unit="months", offset=-1)
        pretty = period.pretty_value
        # Should contain YYYY/MM format
        assert "1 month ago" in pretty
        assert "/" in pretty

    def test_quarters_date_calculation(self):
        """Test quarter date calculation."""
        period = HLedgerPeriod(unit="quarters", offset=0)
        pretty = period.pretty_value
        # Should contain YYYY/QN format
        assert "Q" in pretty

    def test_years_date_calculation(self):
        """Test year date calculation."""
        period = HLedgerPeriod(unit="years", offset=-1)
        pretty = period.pretty_value
        # Should contain YYYY format
        assert "1 year ago" in pretty
        current_year = datetime.now().year
        assert str(current_year - 1) in pretty


class TestHLedgerPeriodEquality:
    """Test period equality."""

    def test_equal_periods(self):
        """Test that identical periods are equal."""
        period1 = HLedgerPeriod(unit="months", offset=0)
        period2 = HLedgerPeriod(unit="months", offset=0)
        assert period1 == period2

    def test_different_units_not_equal(self):
        """Test that periods with different units are not equal."""
        period1 = HLedgerPeriod(unit="months")
        period2 = HLedgerPeriod(unit="weeks")
        assert period1 != period2

    def test_different_offsets_not_equal(self):
        """Test that periods with different offsets are not equal."""
        period1 = HLedgerPeriod(unit="months", offset=0)
        period2 = HLedgerPeriod(unit="months", offset=-1)
        assert period1 != period2

    def test_subdivision_not_affect_equality(self):
        """Test that subdivision doesn't affect equality."""
        period1 = HLedgerPeriod(unit="months", subdivision="weekly")
        period2 = HLedgerPeriod(unit="months", subdivision="monthly")
        # Equality only checks unit and offset
        assert period1 == period2


class TestHLedgerPeriodSubdivision:
    """Test period subdivision."""

    def test_subdivision_options(self):
        """Test different subdivision options."""
        subdivisions = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        for sub in subdivisions:
            period = HLedgerPeriod(subdivision=sub)
            assert period.subdivision == sub
