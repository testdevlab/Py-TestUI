import os

from testui.support import helpers


def test_traceback_keeps_user_frames_when_installed(monkeypatch):
    monkeypatch.chdir(os.path.dirname(os.path.abspath(__file__)))
    installed = os.path.join(
        os.sep, "venv", "site-packages", "testui", "support", "helpers.py"
    )
    monkeypatch.setattr(helpers, "__file__", installed)
    assert "test_helpers.py" in helpers.error_with_traceback("boom")
