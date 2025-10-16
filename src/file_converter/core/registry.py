"""Plugin registry and loader."""
import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable, Optional
import tomli


class Plugin:
    """Represents a loaded plugin."""
    
    def __init__(self, name: str, version: str, config: dict, module: Any):
        self.name = name
        self.version = version
        self.config = config
        self.module = module
        
    def available(self) -> bool:
        """Check if plugin dependencies are available."""
        return self.module.available()
    
    def capabilities(self) -> list[dict]:
        """Get plugin capabilities."""
        return self.module.capabilities()
    
    def plan(self, src_mime: str, dst_mime: str) -> dict:
        """Plan a conversion."""
        return self.module.plan(src_mime, dst_mime)
    
    def run(self, src_path: str, dst_path: str, dst_mime: str, 
            opts: dict, progress_cb: Callable[[str], None]) -> None:
        """Execute a conversion."""
        return self.module.run(src_path, dst_path, dst_mime, opts, progress_cb)


class Registry:
    """Plugin registry."""
    
    def __init__(self):
        self.plugins: list[Plugin] = []
        
    def load_plugins(self, plugin_dir: Path) -> None:
        """
        Load all plugins from the specified directory.
        
        Args:
            plugin_dir: Path to plugins directory
        """
        if not plugin_dir.exists():
            return
            
        for plugin_path in plugin_dir.iterdir():
            if not plugin_path.is_dir():
                continue
                
            toml_file = plugin_path / "plugin.toml"
            py_file = plugin_path / "plugin.py"
            
            if not toml_file.exists() or not py_file.exists():
                continue
                
            try:
                # Load TOML config
                with open(toml_file, "rb") as f:
                    config = tomli.load(f)
                
                # Validate required fields
                required = ["name", "version", "entry", "capabilities", "tool_requires"]
                if not all(k in config for k in required):
                    print(f"Warning: Plugin {plugin_path.name} missing required fields")
                    continue
                
                # Load Python module
                spec = importlib.util.spec_from_file_location(
                    f"file_converter.plugins.{plugin_path.name}",
                    py_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module
                    spec.loader.exec_module(module)
                    
                    # Validate required functions
                    required_funcs = ["available", "capabilities", "plan", "run"]
                    if not all(hasattr(module, f) for f in required_funcs):
                        print(f"Warning: Plugin {plugin_path.name} missing required functions")
                        continue
                    
                    plugin = Plugin(config["name"], config["version"], config, module)
                    self.plugins.append(plugin)
                    
            except Exception as e:
                print(f"Warning: Failed to load plugin {plugin_path.name}: {e}")
    
    def get_available_plugins(self) -> list[Plugin]:
        """Get all available (dependencies met) plugins."""
        return [p for p in self.plugins if p.available()]
    
    def get_plugin_for_conversion(self, src_mime: str, dst_mime: str) -> Optional[Plugin]:
        """
        Find a plugin that can handle the conversion.
        
        Args:
            src_mime: Source MIME type
            dst_mime: Destination MIME type
            
        Returns:
            Plugin or None
        """
        available = self.get_available_plugins()
        
        for plugin in available:
            try:
                # Check if plugin can handle this conversion
                caps = plugin.capabilities()
                for cap in caps:
                    inputs = cap.get("inputs", [])
                    outputs = cap.get("outputs", [])
                    
                    # Check if source matches (with wildcard support)
                    src_match = any(self._mime_match(src_mime, pattern) for pattern in inputs)
                    # Check if destination matches exactly
                    dst_match = dst_mime in outputs
                    
                    if src_match and dst_match:
                        return plugin
            except Exception:
                continue
        
        return None
    
    def _mime_match(self, mime: str, pattern: str) -> bool:
        """Check if MIME matches pattern (supports wildcards like video/*)."""
        if pattern == mime:
            return True
        if pattern.endswith("/*"):
            prefix = pattern[:-2]
            return mime.startswith(prefix + "/")
        return False
    
    def get_all_output_formats(self) -> list[str]:
        """Get all supported output MIME types."""
        formats = set()
        for plugin in self.get_available_plugins():
            try:
                for cap in plugin.capabilities():
                    formats.update(cap.get("outputs", []))
            except Exception:
                continue
        return sorted(formats)
    
    def get_all_input_formats(self) -> list[str]:
        """Get all supported input MIME types/patterns."""
        formats = set()
        for plugin in self.get_available_plugins():
            try:
                for cap in plugin.capabilities():
                    formats.update(cap.get("inputs", []))
            except Exception:
                continue
        return sorted(formats)
