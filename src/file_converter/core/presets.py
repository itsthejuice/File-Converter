"""Preset management for common conversion settings."""
from pathlib import Path
from typing import Optional
import tomli


# Built-in default presets
DEFAULT_PRESETS = {
    'video/mp4': {
        'web_1080p': {
            'crf': 23,
            'preset': 'medium',
            'scale': '1920:1080',
        },
        'web_720p': {
            'crf': 23,
            'preset': 'medium',
            'scale': '1280:720',
        },
        'high_quality': {
            'crf': 18,
            'preset': 'slow',
        },
    },
    'video/webm': {
        'web_1080p': {
            'crf': 30,
            'preset': 'medium',
            'scale': '1920:1080',
        },
    },
    'image/gif': {
        'gif_small': {
            'fps': 12,
            'scale': '480:-1',
        },
        'gif_medium': {
            'fps': 15,
            'scale': '720:-1',
        },
    },
    'audio/mp3': {
        'standard': {
            'quality': 2,
        },
        'high': {
            'quality': 0,
        },
    },
}


def load_defaults(config_path: Optional[str] = None) -> dict:
    """
    Load preset configurations from defaults.toml.
    
    Merges built-in defaults with user customizations.
    
    Args:
        config_path: Path to defaults.toml (default: config/defaults.toml)
        
    Returns:
        Dict of presets organized by MIME type
    """
    presets = DEFAULT_PRESETS.copy()
    
    if config_path is None:
        config_path = "config/defaults.toml"
    
    config_file = Path(config_path)
    if not config_file.exists():
        return presets
    
    try:
        with open(config_file, "rb") as f:
            config = tomli.load(f)
        
        # Merge user presets
        user_presets = config.get("presets", {})
        for mime_type, mime_presets in user_presets.items():
            if mime_type not in presets:
                presets[mime_type] = {}
            presets[mime_type].update(mime_presets)
            
    except Exception as e:
        print(f"Warning: Failed to load presets from {config_path}: {e}")
    
    return presets


def get_preset(mime_type: str, preset_name: str, presets: dict) -> Optional[dict]:
    """
    Get a specific preset configuration.
    
    Args:
        mime_type: Target MIME type
        preset_name: Name of the preset
        presets: Loaded presets dict
        
    Returns:
        Preset options dict or None
    """
    return presets.get(mime_type, {}).get(preset_name)


def list_presets(mime_type: str, presets: dict) -> list[str]:
    """
    List available presets for a MIME type.
    
    Args:
        mime_type: Target MIME type
        presets: Loaded presets dict
        
    Returns:
        List of preset names
    """
    return list(presets.get(mime_type, {}).keys())
