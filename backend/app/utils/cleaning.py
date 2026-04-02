r"""
Data cleaning functions based on data-analysis-report.md Section 6.

Provides reusable cleaning functions for:
- Date field standardization (YYYYMMDD -> YYYY-MM-DD)
- Salary field cleaning (extract numeric values, handle null markers)
- City code parsing (compound codes like "551,-,-")
- Experience/skills parsing (pipe-separated)
- Degree standardization (大专/本科/硕士/博士 -> 1/2/3/4)
- NULL marker standardization (\\N, null, "", whitespace -> None)
- General text cleaning
"""

from typing import Any, Union, List, Optional


def clean_date(value: Union[int, str, None]) -> Optional[str]:
    """
    Convert YYYYMMDD integer/string to YYYY-MM-DD format.

    Returns None for:
    - None input
    - Invalid dates
    - Dates below 19900101 or above 20301231

    Examples:
        clean_date(20190325) -> "2019-03-25"
        clean_date("20190524") -> "2019-05-24"
        clean_date(19891231) -> None
        clean_date("invalid") -> None
    """
    if value is None:
        return None

    try:
        date_str = str(int(value))
    except (ValueError, TypeError):
        return None

    if len(date_str) != 8:
        return None

    try:
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
    except ValueError:
        return None

    if year < 1990 or year > 2030:
        return None

    if month < 1 or month > 12:
        return None

    if day < 1 or day > 31:
        return None

    return f"{year:04d}-{month:02d}-{day:02d}"


def clean_salary(value: Union[int, str, float, None]) -> Optional[int]:
    """
    Clean salary field by extracting numeric value.

    Returns None for:
    - None input
    - Negative values
    - Zero
    - Values exceeding 1,000,000

    Examples:
        clean_salary("8000元/月") -> 8000
        clean_salary("  15000元/月  ") -> 15000
        clean_salary(-7249) -> None
        clean_salary(9999999) -> None
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        numeric_value = int(value)
    else:
        value_str = str(value).strip()
        if not value_str:
            return None

        import re

        match = re.search(r"-?\d+", value_str)
        if not match:
            return None
        numeric_value = int(match.group())

    if numeric_value <= 0:
        return None

    if numeric_value > 1_000_000:
        return None

    return numeric_value


def parse_city_code(value: Optional[str]) -> Union[str, List[str], None]:
    """
    Parse city code, handling compound formats like "551,-,-".

    Returns:
    - None for None or empty input
    - str for simple codes like "551"
    - list of strings for compound codes like "551,-,-" (only valid codes)

    Examples:
        parse_city_code("551") -> "551"
        parse_city_code("551,-,-") -> ["551"]
        parse_city_code("") -> None
    """
    if value is None:
        return None

    value_str = str(value).strip()
    if not value_str:
        return None

    if "-" not in value_str:
        return value_str

    codes = value_str.split(",")
    valid_codes = [code.strip() for code in codes if code.strip() and code.strip() != "-"]

    if not valid_codes:
        return None

    return valid_codes


def parse_experience(value: Optional[str]) -> List[str]:
    """
    Parse experience/skills field from pipe-separated format.

    Returns empty list for:
    - None input
    - Empty string

    Examples:
        parse_experience("停车|现场|凤凰") -> ["停车", "现场", "凤凰"]
        parse_experience("") -> []
        parse_experience("驾驶") -> ["驾驶"]
        parse_experience("  停车 | 现场 | 凤凰  ") -> ["停车", "现场", "凤凰"]
    """
    if value is None:
        return []

    value_str = str(value).strip()
    if not value_str:
        return []

    skills = value_str.split("|")
    cleaned = [skill.strip() for skill in skills if skill.strip()]

    return cleaned


_DEGREE_MAP = {
    "大专": 1,
    "本科": 2,
    "硕士": 3,
    "博士": 4,
}


def standardize_degree(value: Optional[str]) -> Optional[int]:
    """
    Standardize degree text to numeric codes.

    Mapping:
    - 大专 -> 1
    - 本科 -> 2
    - 硕士 -> 3
    - 博士 -> 4

    Returns None for unknown/invalid degrees or None input.

    Examples:
        standardize_degree("大专") -> 1
        standardize_degree("本科") -> 2
        standardize_degree("未知") -> None
    """
    if value is None:
        return None

    value_str = str(value).strip()

    return _DEGREE_MAP.get(value_str)


def clean_null_markers(value: Any) -> Any:
    r"""
    Standardize NULL markers to Python None.

    Converts to None:
    - \\N (backslash-N)
    - "null", "NULL", "Null" (case-insensitive)
    - Empty string ""
    - Whitespace-only strings

    Returns the value unchanged for valid data.

    Examples:
        clean_null_markers("\\N") -> None
        clean_null_markers("null") -> None
        clean_null_markers("NULL") -> None
        clean_null_markers("") -> None
        clean_null_markers("   ") -> None
        clean_null_markers("正常文本") -> "正常文本"
        clean_null_markers("12345") -> "12345"
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    value_str = str(value).strip()

    if not value_str:
        return None

    if value_str == "\\N":
        return None

    if value_str.lower() == "null":
        return None

    return value


def clean_text(value: Optional[str]) -> Optional[str]:
    r"""
    General-purpose text cleaning.

    Performs:
    - Strip leading/trailing whitespace
    - Replace newlines with spaces
    - Standardize quotes

    Returns None for None input or whitespace-only strings.

    Examples:
        clean_text("  some text  ") -> "some text"
        clean_text("line1\\nline2") -> "line1 line2"
    """
    if value is None:
        return None

    value_str = str(value).strip()

    if not value_str:
        return None

    value_str = value_str.replace("\n", " ").replace("\r", " ")
    value_str = value_str.replace(""" """, '"').replace(""" """, '"')
    value_str = " ".join(value_str.split())

    return value_str if value_str else None
