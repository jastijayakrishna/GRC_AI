"""
Unit tests for JSON extraction from LLM output
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import extract_json


def test_extract_simple_json():
    """Test extraction of simple JSON object"""
    text = '{"key": "value"}'
    result = extract_json(text)
    assert result == {"key": "value"}


def test_extract_json_with_preamble():
    """Test extraction when JSON is embedded in text"""
    text = 'Here is the JSON: {"risk": "high", "control": "A.9.4.3"}'
    result = extract_json(text)
    assert result == {"risk": "high", "control": "A.9.4.3"}


def test_extract_json_with_postamble():
    """Test extraction when JSON has trailing text"""
    text = '{"status": "complete"} - end of output'
    result = extract_json(text)
    assert result == {"status": "complete"}


def test_extract_nested_json():
    """Test extraction of nested JSON structures"""
    text = '{"risks": [{"description": "test", "mappings": {"iso": "A.9.4.3"}}]}'
    result = extract_json(text)
    assert "risks" in result
    assert isinstance(result["risks"], list)
    assert "mappings" in result["risks"][0]


def test_extract_json_with_markdown():
    """Test extraction from markdown code blocks"""
    text = '''```json
    {"finding": "weak password", "severity": "high"}
    ```'''
    result = extract_json(text)
    assert result == {"finding": "weak password", "severity": "high"}


def test_extract_malformed_json():
    """Test that malformed JSON returns None"""
    text = '{"incomplete": '
    result = extract_json(text)
    assert result is None


def test_extract_no_json():
    """Test that text without JSON returns None"""
    text = "This is just plain text with no JSON"
    result = extract_json(text)
    assert result is None


def test_extract_array_json():
    """Test extraction of JSON arrays"""
    text = '[{"id": 1}, {"id": 2}]'
    result = extract_json(text)
    assert isinstance(result, list)
    assert len(result) == 2


def test_extract_json_with_special_chars():
    """Test extraction of JSON with special characters"""
    text = '{"description": "Password contains @, #, $, %, &"}'
    result = extract_json(text)
    assert "@" in result["description"]
    assert "#" in result["description"]


def test_extract_json_with_newlines():
    """Test extraction of multiline JSON"""
    text = '''
    {
        "risk": "shared credentials",
        "iso_27001": "A.9.2.4",
        "recommendation": "Implement unique accounts"
    }
    '''
    result = extract_json(text)
    assert result["risk"] == "shared credentials"
    assert result["iso_27001"] == "A.9.2.4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
