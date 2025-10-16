"""Conversion planning and routing."""
from typing import Optional
from .registry import Registry, Plugin


def plan_conversion(src_mime: str, dst_mime: str, registry: Registry) -> Optional[dict]:
    """
    Plan a conversion from source to destination MIME type.
    
    For MVP, only direct edge planning (single plugin).
    Multi-hop planning is TODO.
    
    Args:
        src_mime: Source MIME type
        dst_mime: Destination MIME type
        registry: Plugin registry
        
    Returns:
        Dict with 'plugin' and 'plan' or None if no route found
    """
    plugin = registry.get_plugin_for_conversion(src_mime, dst_mime)
    
    if plugin is None:
        return None
    
    try:
        plan = plugin.plan(src_mime, dst_mime)
        return {
            'plugin': plugin,
            'plan': plan,
            'src_mime': src_mime,
            'dst_mime': dst_mime
        }
    except Exception as e:
        print(f"Error planning conversion with {plugin.name}: {e}")
        return None


def get_supported_outputs(src_mime: str, registry: Registry) -> list[str]:
    """
    Get all supported output formats for a given source MIME type.
    
    Args:
        src_mime: Source MIME type
        registry: Plugin registry
        
    Returns:
        List of supported destination MIME types
    """
    outputs = set()
    
    for plugin in registry.get_available_plugins():
        try:
            caps = plugin.capabilities()
            for cap in caps:
                inputs = cap.get("inputs", [])
                
                # Check if this plugin supports the source
                src_match = any(
                    registry._mime_match(src_mime, pattern) 
                    for pattern in inputs
                )
                
                if src_match:
                    outputs.update(cap.get("outputs", []))
        except Exception:
            continue
    
    return sorted(outputs)
