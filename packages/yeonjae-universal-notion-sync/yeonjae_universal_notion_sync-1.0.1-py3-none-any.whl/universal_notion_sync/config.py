"""Configuration management for Notion sync."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from .models import NotionPage

logger = logging.getLogger(__name__)


class NotionSyncConfig:
    """Manage Notion sync configuration."""
    
    def __init__(self, config_file: str = "notion_sync_config.json"):
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            except Exception as exc:
                logger.error(f"Failed to load config: {exc}")
        
        # Return default config
        return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            "token": "",  # To be set via environment variable
            "pages": [],
            "sync_interval_minutes": 30,
            "auto_update_rules": True
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration."""
        return self.config
    
    def get_targets(self) -> List[Dict[str, Any]]:
        """Get sync targets."""
        return self.config.get("targets", [])
    
    def get_credentials(self) -> Dict[str, Any]:
        """Get Notion credentials."""
        return self.config.get("notion_credentials", {})
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, default=str)
            logger.info(f"✅ Saved Notion sync config to {self.config_file}")
        except Exception as exc:
            logger.error(f"❌ Failed to save config: {exc}")
            raise


# Global config manager instance
config_manager = NotionSyncConfig()
