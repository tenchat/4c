"""
Tests for data cleaning functions (TDD approach).

These tests define the expected behavior of cleaning functions
based on the data analysis report Section 6.

Run with: pytest backend/tests/test_cleaning_functions.py -v
"""

import pytest
from backend.app.utils.cleaning import (
    clean_date,
    clean_salary,
    parse_city_code,
    parse_experience,
    standardize_degree,
    clean_null_markers,
)


class TestCleanDate:
    """Test date cleaning: YYYYMMDD -> YYYY-MM-DD"""

    def test_valid_date(self):
        """Valid date should be converted to standard format"""
        assert clean_date(20190325) == "2019-03-25"

    def test_date_with_string_input(self):
        """String date should also be converted"""
        assert clean_date("20190524") == "2019-05-24"

    def test_invalid_date(self):
        """Invalid date should return None"""
        assert clean_date("invalid") is None

    def test_date_out_of_range_low(self):
        """Date below 19900101 should return None"""
        assert clean_date(19891231) is None

    def test_date_out_of_range_high(self):
        """Date above 20301231 should return None"""
        assert clean_date(20310101) is None

    def test_none_input(self):
        """None input should return None"""
        assert clean_date(None) is None


class TestCleanSalary:
    """Test salary field cleaning"""

    def test_salary_with_unit_string(self):
        """Salary string with unit should extract numeric value"""
        assert clean_salary("8000元/月") == 8000

    def test_salary_with_whitespace(self):
        """Salary with whitespace should be cleaned"""
        assert clean_salary("  15000元/月  ") == 15000

    def test_negative_salary(self):
        """Negative salary should return None"""
        assert clean_salary(-7249) is None

    def test_excessive_salary(self):
        """Salary exceeding 1000000 should return None"""
        assert clean_salary(9999999) is None

    def test_reasonable_salary(self):
        """Reasonable salary should pass through"""
        assert clean_salary(25000) == 25000

    def test_zero_salary(self):
        """Zero salary should return None"""
        assert clean_salary(0) is None

    def test_none_input(self):
        """None input should return None"""
        assert clean_salary(None) is None


class TestParseCityCode:
    """Test city code parsing"""

    def test_simple_city_code(self):
        """Simple city code should return as-is"""
        assert parse_city_code("551") == "551"

    def test_compound_city_code(self):
        """Compound city code should extract first valid code"""
        result = parse_city_code("551,-,-")
        assert result == ["551"]

    def test_none_input(self):
        """None input should return None"""
        assert parse_city_code(None) is None

    def test_empty_string(self):
        """Empty string should return None"""
        assert parse_city_code("") is None


class TestParseExperience:
    """Test experience/skills parsing"""

    def test_pipe_separated_skills(self):
        """Pipe-separated skills should be split into list"""
        result = parse_experience("停车|现场|凤凰")
        assert result == ["停车", "现场", "凤凰"]

    def test_empty_string(self):
        """Empty string should return empty list"""
        assert parse_experience("") == []

    def test_single_skill(self):
        """Single skill without pipe should return single-item list"""
        assert parse_experience("驾驶") == ["驾驶"]

    def test_whitespace_stripping(self):
        """Skills should have whitespace stripped"""
        result = parse_experience("  停车 | 现场 | 凤凰  ")
        assert "停车" in result
        assert "现场" in result
        assert "凤凰" in result

    def test_none_input(self):
        """None input should return empty list"""
        assert parse_experience(None) == []


class TestStandardizeDegree:
    """Test degree standardization"""

    def test_associate_degree(self):
        """大专 should map to 1"""
        assert standardize_degree("大专") == 1

    def test_bachelor_degree(self):
        """本科 should map to 2"""
        assert standardize_degree("本科") == 2

    def test_master_degree(self):
        """硕士 should map to 3"""
        assert standardize_degree("硕士") == 3

    def test_doctoral_degree(self):
        """博士 should map to 4"""
        assert standardize_degree("博士") == 4

    def test_unknown_degree(self):
        """未知 or unrecognized should return None"""
        assert standardize_degree("未知") is None

    def test_invalid_degree(self):
        """Invalid degree should return None"""
        assert standardize_degree("高中") is None

    def test_case_insensitive(self):
        """Degree matching should be case-insensitive for safety"""
        assert standardize_degree("本科") == 2

    def test_none_input(self):
        """None input should return None"""
        assert standardize_degree(None) is None


class TestCleanNullMarkers:
    """Test NULL marker standardization"""

    def test_backslash_n_marker(self):
        """\\N marker should return None"""
        assert clean_null_markers("\\N") is None

    def test_null_string(self):
        """null string (case-insensitive) should return None"""
        assert clean_null_markers("null") is None
        assert clean_null_markers("NULL") is None
        assert clean_null_markers("Null") is None

    def test_empty_string(self):
        """Empty string should return None"""
        assert clean_null_markers("") is None

    def test_normal_text(self):
        """Normal text should pass through unchanged"""
        assert clean_null_markers("正常文本") == "正常文本"

    def test_whitespace_only(self):
        """Whitespace-only string should return None"""
        assert clean_null_markers("   ") is None

    def test_numeric_string(self):
        """Numeric string should pass through"""
        assert clean_null_markers("12345") == "12345"

    def test_none_input(self):
        """None input should return None"""
        assert clean_null_markers(None) is None
