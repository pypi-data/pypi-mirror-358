import os
import tempfile
import pytest
from robust_toml_config import TOMLConfig


def test_create_config():
    """Test creating a new config file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={"app": {"name": "TestApp"}})
        assert config.get("app.name") == "TestApp"


def test_get_set_value():
    """Test getting and setting values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={})
        config.set("key", "value")
        assert config.get("key") == "value"


def test_autosave():
    """Test autosave functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={})
        config.set("key", "value")

        # Reload and verify
        config2 = TOMLConfig(file_path)
        assert config2.get("key") == "value"


def test_get_section():
    """Test getting an entire section."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={
            "database": {
                "host": "localhost",
                "port": 3306
            }
        })
        section = config.get_section("database")
        assert section["host"] == "localhost"
        assert section["port"] == 3306


def test_update_section():
    """Test updating an entire section."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={"section": {"key1": "value1"}})

        config.update_section("section", {"key1": "updated", "key2": "new"})

        assert config.get("section.key1") == "updated"
        assert config.get("section.key2") == "new"