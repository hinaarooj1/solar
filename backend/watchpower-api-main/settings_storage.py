import json
import os
from typing import Any, Dict
from datetime import datetime

class SettingsStorage:
    """Simple JSON file storage for system settings"""
    
    def __init__(self, filepath: str = "system_settings.json"):
        self.filepath = filepath
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self._default_settings()
        return self._default_settings()
    
    def _default_settings(self) -> Dict[str, Any]:
        """Return default settings"""
        return {
            "grid_feeding_enabled": True,
            "output_priority": "Solar_first",
            "lcd_auto_return_enabled": True,
            "lcd_timeout_seconds": 60,
            "last_updated": None
        }
    
    def save_settings(self) -> bool:
        """Save settings to JSON file"""
        try:
            self.settings["last_updated"] = datetime.now().isoformat()
            with open(self.filepath, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a setting value and save"""
        self.settings[key] = value
        return self.save_settings()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Update multiple settings at once"""
        self.settings.update(updates)
        return self.save_settings()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()


# Global storage instance
settings_storage = SettingsStorage()










