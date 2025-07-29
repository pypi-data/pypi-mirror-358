try:
    from .qt_app import QTApplication
    from .qt_color_picker import select_color
    from .qt_input_dialog import get_text

    __all__ = ["QTApplication", "select_color", "get_text"]
except ImportError as e:
    raise ImportError("PyQt6 is required for GUI functionality. Install it with: pip install bear-utils[gui]") from e
