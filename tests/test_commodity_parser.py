"""Tests for commodity and amount parsing."""

import pytest

from hledger_tui.core.parser import CommodityParser, ParsedAmount


class TestCommodityParser:
    """Test CommodityParser for various HLedger commodity styles."""

    def test_parse_symbol_first_euro(self):
        """Test parsing euro symbol before amount."""
        result = CommodityParser.parse("€ 1,000.00")
        assert result.numeric_value == 1000.00
        assert result.commodity == "€"

    def test_parse_symbol_first_dollar(self):
        """Test parsing dollar symbol before amount."""
        result = CommodityParser.parse("$ 100.50")
        assert result.numeric_value == 100.50
        assert result.commodity == "$"

    def test_parse_symbol_last_eur(self):
        """Test parsing EUR code after amount."""
        result = CommodityParser.parse("1,000.00 EUR")
        assert result.numeric_value == 1000.00
        assert result.commodity == "EUR"

    def test_parse_symbol_first_usd_no_spaces(self):
        """Test parsing USD code after amount."""
        result = CommodityParser.parse("USD100.50")
        assert result.numeric_value == 100.50
        assert result.commodity == "USD"

    def test_parse_symbol_last_usd(self):
        """Test parsing USD code after amount."""
        result = CommodityParser.parse("100.50 USD")
        assert result.numeric_value == 100.50
        assert result.commodity == "USD"

    def test_parse_european_format_comma_decimal(self):
        """Test European format with comma as decimal separator."""
        result = CommodityParser.parse("₺1.000,00")
        assert result.numeric_value == 1000.00
        assert result.commodity == "₺"

    def test_parse_euro_european_format(self):
        """Test euro with European format."""
        result = CommodityParser.parse("€1,000.00")
        assert result.numeric_value == 1000.00
        assert result.commodity == "€"

    def test_parse_space_separated_thousands(self):
        """Test space-separated thousands separator."""
        result = CommodityParser.parse("1 000,00 ₸")
        assert result.numeric_value == 1000.00
        assert result.commodity == "₸"

    def test_parse_gbp(self):
        """Test British pounds."""
        result = CommodityParser.parse("£1,000.00")
        assert result.numeric_value == 1000.00
        assert result.commodity == "£"

    def test_parse_multi_char_commodity_first(self):
        """Test multi-character commodity before amount."""
        result = CommodityParser.parse("Fr 1000.00")
        assert result.numeric_value == 1000.00
        assert result.commodity == "Fr"

    def test_parse_multi_digit_decimal_spaces(self):
        """Test with three decimal places and spaces."""
        result = CommodityParser.parse("1,000.000 دت")
        assert result.numeric_value == 1000.000
        assert result.commodity == "دت"

    def test_parse_bulgarian_lev(self):
        """Test Bulgarian lev format."""
        result = CommodityParser.parse("1.000,00 лв")
        assert result.numeric_value == 1000.00
        assert result.commodity == "лв"

    def test_parse_russian_ruble(self):
        """Test Russian ruble format."""
        result = CommodityParser.parse("1 000,00 ₽")
        assert result.numeric_value == 1000.00
        assert result.commodity == "₽"

    def test_parse_turkish_lira_with_decimals(self):
        """Test Turkish lira with decimal places."""
        result = CommodityParser.parse("₺1.904,22")
        assert result.numeric_value == 1904.22
        assert result.commodity == "₺"

    def test_parse_euro_large_amount(self):
        """Test euro with large amount."""
        result = CommodityParser.parse("€5000.00")
        assert result.numeric_value == 5000.00
        assert result.commodity == "€"

    def test_parse_negative_amount(self):
        """Test parsing negative amounts."""
        result = CommodityParser.parse("$ -500.00")
        assert result.numeric_value == -500.00
        assert result.commodity == "$"

    def test_parse_negative_amount_symbol_last(self):
        """Test parsing negative amounts with symbol last."""
        result = CommodityParser.parse("-1,000.00 EUR")
        assert result.numeric_value == -1000.00
        assert result.commodity == "EUR"

    def test_parse_positive_sign(self):
        """Test parsing amounts with explicit positive sign."""
        result = CommodityParser.parse("+100.00 USD")
        assert result.numeric_value == 100.00
        assert result.commodity == "USD"

    def test_parse_multiple_spaces_between_amount_and_commodity(self):
        """Test multiple spaces between amount and commodity."""
        result = CommodityParser.parse("100.00   EUR")
        assert result.numeric_value == 100.00
        assert result.commodity == "EUR"

    def test_parse_large_number_space_separated(self):
        """Test very large numbers with space separators."""
        result = CommodityParser.parse("1 000 000,00 EUR")
        assert result.numeric_value == 1000000.00
        assert result.commodity == "EUR"

    def test_parse_mixed_space_comma_separators(self):
        """Test mixed space and comma thousand separators."""
        result = CommodityParser.parse("€ 1 000 000,50")
        assert result.numeric_value == 1000000.50
        assert result.commodity == "€"

    def test_parse_no_decimal_places(self):
        """Test amounts without decimal places."""
        result = CommodityParser.parse("1000 USD")
        assert result.numeric_value == 1000.00
        assert result.commodity == "USD"

    def test_parse_small_decimal_amount(self):
        """Test small decimal amounts."""
        result = CommodityParser.parse("€ 0.50")
        assert result.numeric_value == 0.50
        assert result.commodity == "€"

    def test_parse_leading_trailing_spaces(self):
        """Test with leading and trailing spaces."""
        result = CommodityParser.parse("   € 100.00   ")
        assert result.numeric_value == 100.00
        assert result.commodity == "€"

    def test_parse_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Empty amount string"):
            CommodityParser.parse("")

    def test_parse_no_numeric_part_raises_error(self):
        """Test that string with no numeric part raises ValueError."""
        with pytest.raises(ValueError, match="No numeric part found"):
            CommodityParser.parse("EUR USD")

    def test_parse_zero_amount(self):
        """Test parsing zero amount."""
        result = CommodityParser.parse("€ 0")
        assert result.numeric_value == 0.0
        assert result.commodity == "€"

    def test_parse_only_numeric_no_commodity(self):
        """Test parsing numeric-only string (no commodity)."""
        result = CommodityParser.parse("100.50")
        assert result.numeric_value == 100.50
        assert result.commodity == ""

    def test_parse_complex_multi_space_euro_style(self):
        """Test complex European format with multiple space separators."""
        result = CommodityParser.parse("€ 1 234 567,89")
        assert result.numeric_value == 1234567.89
        assert result.commodity == "€"

    def test_parse_complex_multi_comma_us_style(self):
        """Test complex US format with multiple comma separators."""
        result = CommodityParser.parse("$1,234,567.89")
        assert result.numeric_value == 1234567.89
        assert result.commodity == "$"

    def test_result_is_named_tuple(self):
        """Test that result is a ParsedAmount NamedTuple."""
        result = CommodityParser.parse("€ 100.00")
        assert isinstance(result, ParsedAmount)
        assert result.numeric_value == 100.00
        assert result.commodity == "€"
