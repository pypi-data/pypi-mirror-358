import pytest
import os
import time
import orjson
from configflow import ConfigFlow


@pytest.fixture
def temp_config(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {"port": 8080, "debug": True}
    with open(config_path, "wb") as f:
        f.write(orjson.dumps(config_data))
    return config_path


def test_load_config(temp_config):
    config = ConfigFlow(temp_config)
    result = config.load(schema={"port": int, "debug": bool})
    assert result == {"port": 8080, "debug": True}


def test_validation_error(temp_config):
    config = ConfigFlow(temp_config)
    with pytest.raises(ValueError, match="Config validation failed"):
        config.load(schema={"port": str})

def test_load_env_config(tmp_path):
    config_path = tmp_path / ".env"
    config_data = "PORT=8080\nDEBUG=True\n"
    with open(config_path, "w") as f:
        f.write(config_data)
    config = ConfigFlow(config_path)
    result = config.load(schema={"PORT": int, "DEBUG": bool})
    assert result == {"PORT": 8080, "DEBUG": True}


def test_on_change(temp_config):
    config = ConfigFlow(temp_config)
    changes = []

    @config.on_change
    def callback(new_config):
        changes.append(new_config)

    config.load()
    config.watch()

    # Simulate a file change
    time.sleep(0.1)  # Ensure watchdog is ready
    with open(temp_config, "wb") as f:
        f.write(orjson.dumps({"port": 9090, "debug": False}))

    time.sleep(0.5)  # Wait for watchdog to detect
    config.stop()

    assert len(changes) > 0
    assert changes[-1] == {"port": 9090, "debug": False}
