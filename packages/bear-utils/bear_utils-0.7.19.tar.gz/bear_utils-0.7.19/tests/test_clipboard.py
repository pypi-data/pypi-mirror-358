from unittest.mock import patch

import pytest

from src.bear_utils.extras._tools import ClipboardManager
from bear_utils.extras.platform_utils import OS


@patch("src.bear_utils.extras._tools.get_platform", return_value=OS.DARWIN)
def test_macos_commands(mock_platform):
    manager = ClipboardManager()
    assert manager._copy.cmd == "pbcopy"
    assert manager._paste.cmd == "pbpaste"


@patch("src.bear_utils.extras._tools.shutil.which")
@patch("src.bear_utils.extras._tools.get_platform", return_value=OS.LINUX)
def test_linux_wayland(mock_platform, mock_which):
    mock_which.side_effect = lambda name: f"/usr/bin/{name}" if name in {"wl-copy", "wl-paste"} else None
    manager = ClipboardManager()
    assert manager._copy.cmd == "wl-copy"
    assert manager._paste.cmd == "wl-paste"


@patch("src.bear_utils.extras._tools.shutil.which")
@patch("src.bear_utils.extras._tools.get_platform", return_value=OS.LINUX)
def test_linux_xclip(mock_platform, mock_which):
    def which(name: str):
        if name == "xclip":
            return "/usr/bin/xclip"
        return None

    mock_which.side_effect = which
    manager = ClipboardManager()
    assert manager._copy.cmd == "xclip -selection clipboard"
    assert manager._paste.cmd == "xclip -selection clipboard -o"


@patch("src.bear_utils.extras._tools.shutil.which", return_value=None)
@patch("src.bear_utils.extras._tools.get_platform", return_value=OS.LINUX)
def test_linux_no_clipboard(mock_platform, mock_which):
    with pytest.raises(RuntimeError):
        ClipboardManager()


@patch("src.bear_utils.extras._tools.get_platform", return_value=OS.WINDOWS)
def test_windows_commands(mock_platform):
    manager = ClipboardManager()
    assert manager._copy.cmd == "clip"
    assert manager._paste.cmd == "powershell Get-Clipboard"
