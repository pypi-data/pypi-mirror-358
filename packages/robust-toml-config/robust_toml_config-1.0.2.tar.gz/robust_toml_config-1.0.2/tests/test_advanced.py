import os
import tempfile
from robust_toml_config import TOMLConfig


def test_nested_config():
    """Test nested configuration paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={})
        config.set("a.b.c", 42)
        assert config.get("a.b.c") == 42


def test_batch_update():
    """Test batch update context manager."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={}, autosave=True)

        with config.batch_update():
            config.set("key1", "value1")
            config.set("key2", "value2")

        # Verify both values were saved
        config2 = TOMLConfig(file_path)
        assert config2.get("key1") == "value1"
        assert config2.get("key2") == "value2"


def test_ensure_type():
    """Test type safety checks."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={"num": "not a number"})

        # Should correct type
        num = config.ensure_type("num", int, 10)
        assert num == 10
        assert config.get("num") == 10


def test_to_dict():
    """Test conversion to dictionary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.toml")
        config = TOMLConfig(file_path, default_data={
            "section": {
                "key": "value",
                "nested": {"num": 42}
            }
        })

        config_dict = config.to_dict()
        assert config_dict["section"]["key"] == "value"
        assert config_dict["section"]["nested"]["num"] == 42