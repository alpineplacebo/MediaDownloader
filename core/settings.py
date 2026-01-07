import json
import os
from pathlib import Path

class SettingsManager:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.default_download_path = str(Path.home() / "Downloads")
        self.settings = self._load_settings()

    def _load_settings(self):
        if not os.path.exists(self.filename):
            return {"download_path": self.default_download_path}
        
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"download_path": self.default_download_path}

    def save_settings(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except IOError:
            print("Failed to save settings")

    def get_download_path(self):
        return self.settings.get("download_path", self.default_download_path)

    def set_download_path(self, path):
        self.settings["download_path"] = str(path)
        self.save_settings()

    def get_cookies_browser(self):
        return self.settings.get("cookies_browser", "None")

    def set_cookies_browser(self, browser):
        self.settings["cookies_browser"] = browser
        self.save_settings()
