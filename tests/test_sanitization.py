"""
Unit tests for input sanitization functions
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import sanitize_input, MAX_INPUT_LENGTH


def test_sanitize_normal_text():
    """Test sanitization of normal audit text"""
    text = "DevOps team uses shared credentials for production access"
    result = sanitize_input(text)
    assert result == text
    assert isinstance(result, str)


def test_sanitize_removes_null_bytes():
    """Test that null bytes are removed"""
    text = "test\x00data\x00here"
    result = sanitize_input(text)
    assert result == "testdatahere"
    assert "\x00" not in result


def test_sanitize_removes_control_characters():
    """Test that control characters are removed"""
    text = "test\x01\x02\x03data"
    result = sanitize_input(text)
    assert result == "testdata"


def test_sanitize_preserves_newlines():
    """Test that newlines and tabs are preserved"""
    text = "line1\nline2\ttabbed"
    result = sanitize_input(text)
    assert "\n" in result
    assert "\t" in result


def test_sanitize_strips_whitespace():
    """Test that leading/trailing whitespace is removed"""
    text = "   data with spaces   "
    result = sanitize_input(text)
    assert result == "data with spaces"


def test_sanitize_too_long_input():
    """Test that input exceeding max length is rejected"""
    text = "a" * (MAX_INPUT_LENGTH + 1)
    result = sanitize_input(text)
    assert result is None


def test_sanitize_max_length_input():
    """Test that input at exactly max length is accepted"""
    text = "a" * MAX_INPUT_LENGTH
    result = sanitize_input(text)
    assert result is not None
    assert len(result) == MAX_INPUT_LENGTH


def test_sanitize_empty_input():
    """Test that empty input is rejected"""
    result = sanitize_input("")
    assert result is None


def test_sanitize_whitespace_only():
    """Test that whitespace-only input is rejected"""
    result = sanitize_input("   \n\t   ")
    assert result is None


def test_sanitize_special_characters():
    """Test that legitimate special characters are preserved"""
    text = "Password: Admin@123! for server 192.168.1.1"
    result = sanitize_input(text)
    assert "@" in result
    assert "!" in result
    assert "." in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
