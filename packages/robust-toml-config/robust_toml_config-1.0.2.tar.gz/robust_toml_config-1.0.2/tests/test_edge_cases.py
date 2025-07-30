import os
import tempfile
import pytest
from robust_toml_config import TOMLConfig


def test_missing_file():
    """Test handling of missing file when create_if_missing=False."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "missing.toml")
        with pytest.raises(FileNotFoundError):
            TOMLConfig(file_path, create_if_missing=False)


def test_encoding_fallback():
    """Test encoding fallback mechanism."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")

        # Write a file with UTF-16 encoding
        with open(file_path, "w", encoding="utf-16") as f:
            f.write('key = "value"')

        # Should fail to read with default UTF-8
        with pytest.raises(UnicodeDecodeError):
            TOMLConfig(file_path)

        # But should work with explicit encoding
        config = TOMLConfig(file_path, encoding="utf-16")
        assert config.get("key") == "value"


def test_non_dict_section():
    """Test getting a section that's not a dictionary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={"section": "not a dict"})

        # Should return default when getting section
        section = config.get_section("section", default={"key": "value"})
        assert section == {"key": "value"}


def test_dot_path_edge_cases():
    """Test edge cases with dot paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={})

        # Test empty path
        assert config.get("") is None

        # Test single segment path
        config.set("key", "value")
        assert config.get("key") == "value"

        # Test path with empty segments
        config.set("a..b", "value")
        assert config.get("a..b") == "value"