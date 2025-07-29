import pytest
from chameli.config import load_config, get_config
from chameli import get_default_config_path


def test_load_config():
    """Test that the configuration file loads successfully."""
    config_path = get_default_config_path()
    load_config(config_path)
    config = get_config()
    assert config is not None


def test_top_level_keys():
    """Test that top-level keys in the configuration are accessible."""
    config = get_config()
    assert "markets" in config.configs
    assert isinstance(config.get("markets"), dict)


def test_nested_properties():
    """Test that nested properties in the configuration are accessible."""
    config = get_config()
    nse_market = config.get("markets", {}).get("NSE", {})
    assert nse_market.get("open_time") == "09:15:00"
    assert nse_market.get("close_time") == "15:30:00"


def test_missing_keys():
    """Test that accessing a missing key returns None or a default value."""
    config = get_config()
    assert config.get("non_existent_key") is None
    assert config.get("non_existent_key", "default_value") == "default_value"


def test_file_not_found():
    """Test that a FileNotFoundError is raised for an invalid file path."""
    with pytest.raises(FileNotFoundError):
        load_config("/invalid/path/to/config.yaml", force_reload=True)
