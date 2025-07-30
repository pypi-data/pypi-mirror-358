import json
from pathlib import Path
from watchdog.observers import Observer
"""
MiniMocker – Configuration loader and file watcher

© 2025 SkillSetPRO – All rights reserved under the MIT License.
"""

from watchdog.events import FileSystemEventHandler
from .utils import log

class ConfigWatcher(FileSystemEventHandler):
    def __init__(self, config_path, on_reload):
        self.config_path = config_path
        self.on_reload = on_reload

    def on_modified(self, event):
        if event.src_path == str(self.config_path.resolve()):
            log("Configuration file changed. Reloading...")
            self.on_reload()

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def watch_config(config_path, on_reload):
    observer = Observer()
    event_handler = ConfigWatcher(config_path, on_reload)
    observer.schedule(event_handler, path=str(Path(config_path).parent), recursive=False)
    observer.start()
    return observer
