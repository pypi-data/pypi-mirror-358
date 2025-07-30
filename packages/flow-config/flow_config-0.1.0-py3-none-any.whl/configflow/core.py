import os
import time
from typing import Callable, Dict, Optional, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .parsers import parse_config
from .validators import validate_config


class ConfigFlow:
    """A class to manage configuration files with real-time monitoring and event-driven updates."""

    def __init__(self, config_path: str):
        """Initialize ConfigFlow with a config file path."""
        self.config_path = os.path.abspath(config_path)
        self.config = None
        self.schema = None
        self.callbacks = []
        self.observer = None
        self._last_modified = 0

    def load(self, schema: Optional[Dict[str, type]] = None) -> Dict[str, Any]:
        """Load and validate the config file."""
        self.schema = schema
        self.config = parse_config(self.config_path)
        if self.schema:
            self.config = validate_config(self.config, self.schema)
        return self.config

    def on_change(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback to be called when the config changes."""
        self.callbacks.append(callback)

    def watch(self) -> None:
        """Start monitoring the config file for changes."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        self.observer = Observer()
        handler = ConfigChangeHandler(self)
        self.observer.schedule(
            handler, os.path.dirname(self.config_path), recursive=False
        )
        self.observer.start()

    def stop(self) -> None:
        """Stop monitoring the config file."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

    def _handle_change(self) -> None:
        """Handle a config file change by reloading and notifying callbacks."""
        try:
            mtime = os.path.getmtime(self.config_path)
            if mtime <= self._last_modified:
                return
            self._last_modified = mtime

            new_config = parse_config(self.config_path)
            if self.schema:
                new_config = validate_config(new_config, self.schema)

            if new_config != self.config:
                self.config = new_config
                for callback in self.callbacks:
                    callback(self.config)
        except Exception as e:
            print(f"Error handling config change: {e}")


class ConfigChangeHandler(FileSystemEventHandler):
    """Watchdog handler for config file changes."""

    def __init__(self, config_flow: ConfigFlow):
        self.config_flow = config_flow

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.config_flow.config_path:
            self.config_flow._handle_change()
