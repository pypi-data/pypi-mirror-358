try:
    from .gui_tools import QTApplication, get_text, select_color

    __all__ = ["QTApplication", "select_color", "get_text"]
except ImportError as e:
    raise ImportError("PyQt6 is required for GUI functionality. Install it with: pip install bear-utils[gui]") from e
