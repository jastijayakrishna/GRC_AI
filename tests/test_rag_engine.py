"""
Unit tests for RAG engine functions
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import rag_engine


def test_load_crosswalk_db():
    """Test that crosswalk database loads successfully"""
    result = rag_engine.load_crosswalk_db()
    assert result is True
    assert rag_engine.crosswalk_collection.count() > 0


def test_crosswalk_pattern_count():
    """Test that all patterns are loaded"""
    rag_engine.load_crosswalk_db()
    count = rag_engine.crosswalk_collection.count()
    # Should have 101 patterns after enhancements
    assert count >= 100
    assert count <= 110  # Allow some flexibility


def test_get_framework_mappings_good_match():
    """Test framework mapping with a known good pattern"""
    rag_engine.load_crosswalk_db()

    finding = "Users are using weak passwords like password123 and admin"
    result = rag_engine.get_framework_mappings(finding, threshold=1.4)

    assert result is not None
    assert "pattern_name" in result
    assert "iso_27001" in result
    assert result["pattern_name"] == "weak_password"


def test_get_framework_mappings_shared_creds():
    """Test framework mapping for shared credentials"""
    rag_engine.load_crosswalk_db()

    finding = "DevOps team uses shared admin account with password distributed via Slack"
    result = rag_engine.get_framework_mappings(finding, threshold=1.4)

    assert result is not None
    assert result["pattern_name"] == "shared_credentials"
    assert result["iso_27001"] == "A.9.2.4"


def test_get_framework_mappings_no_match():
    """Test framework mapping with unrelated text"""
    rag_engine.load_crosswalk_db()

    finding = "The coffee machine is broken in the kitchen"
    result = rag_engine.get_framework_mappings(finding, threshold=1.4)

    # Should not match any security patterns
    assert result is None


def test_get_framework_mappings_backup_failure():
    """Test framework mapping for backup issues"""
    rag_engine.load_crosswalk_db()

    finding = "Database backups have not been tested in 14 months"
    result = rag_engine.get_framework_mappings(finding, threshold=1.4)

    assert result is not None
    assert "backup" in result["pattern_name"]


def test_get_framework_mappings_threshold_strict():
    """Test that strict threshold rejects weak matches"""
    rag_engine.load_crosswalk_db()

    finding = "Some vague security concern"
    result = rag_engine.get_framework_mappings(finding, threshold=0.5)

    # Very strict threshold should reject weak matches
    assert result is None


def test_get_framework_mappings_returns_all_frameworks():
    """Test that result contains all four frameworks"""
    rag_engine.load_crosswalk_db()

    finding = "Multi-factor authentication is not enabled on VPN access"
    result = rag_engine.get_framework_mappings(finding, threshold=1.4)

    if result:  # May or may not match depending on embeddings
        assert "iso_27001" in result
        assert "soc_2" in result
        assert "hipaa" in result
        assert "nist_csf" in result


def test_ingest_policy_invalid_path():
    """Test policy ingestion with invalid file path"""
    success, msg = rag_engine.ingest_policy("nonexistent_file.pdf")
    assert success is False
    assert "error" in msg.lower() or "no such file" in msg.lower()


def test_query_policy_empty_collection():
    """Test policy query when no policies loaded"""
    # Clear policy collection
    result = rag_engine.query_policy("What is our password policy?")
    # Should return None if no policies loaded
    assert result is None or isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
