"""WRD (WRonai Development) - A powerful workflow automation tool for developers."""

import sys
from typing import TYPE_CHECKING, Any

# Import version info
from .__version__ import __author__, __email__, __version__

# Lazy imports to prevent circular imports during build
if not TYPE_CHECKING and not sys.version_info >= (3, 7):
    from importlib import import_module

    def __getattr__(name: str) -> Any:
        if name in {"WRDShell", "TemplateManager", "get_template_manager"}:
            import importlib

            module = importlib.import_module(
                f"wrd.{name.lower()}"
                if name != 'get_template_manager'
                else 'wrd.template_manager'
            )
            return getattr(module, name)
        raise AttributeError(f"module 'wrd' has no attribute '{name}'")

else:
    try:
        from .cli import WRDShell
        from .template_manager import TemplateManager, get_template_manager
    except ImportError:
        # This can happen during build time
        WRDShell = None  # type: ignore
        TemplateManager = None  # type: ignore
        get_template_manager = None  # type: ignore

__all__ = [
    '__version__',
    '__author__',
    '__email__',
    'WRDShell',
    'TemplateManager',
    'get_template_manager',
]

__license__ = "Apache-2.0"
