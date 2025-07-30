# ruff: noqa: F401
# macdefaultbrowsy/__init__.py

"""A Python port of macdefaultbrowser to manage the default web browser on macOS."""

from .macdefaultbrowsy import (
    get_available_browsers,
    get_default_browser,
    set_default_browser,
    print_browsers_list,
)

from .__version__ import __version__

__all__ = ["get_available_browsers", "get_default_browser", "set_default_browser", "print_browsers_list"]
