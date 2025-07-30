# %%
import shutil
import subprocess

from depsize.depsize import get_pip_packages


# %%
class FakeResult:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.returncode = returncode


def test_uv_installed(monkeypatch):
    """
    Should run 'uv pip list' when uv is found
    """
    monkeypatch.setattr(shutil, "which", lambda cmd: cmd == "uv")

    def fake_run(*args, **kwargs):
        return FakeResult('[{"name": "foo", "version": "1.0.0"}]', 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = get_pip_packages()
    assert result == [{"name": "foo", "version": "1.0.0"}]


def test_pip_installed_if_uv_not_found(monkeypatch):
    """
    Should fallback to 'pip list' if uv is not found
    """
    monkeypatch.setattr(shutil, "which", lambda cmd: cmd == "pip")

    def fake_run(*args, **kwargs):
        return FakeResult('[{"name": "bar", "version": "2.0.0"}]', 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = get_pip_packages()
    assert result == [{"name": "bar", "version": "2.0.0"}]


def test_poetry_fallback_message(monkeypatch, capsys):
    """
    Should print an error message if poetry is found but not pip or uv
    """
    monkeypatch.setattr(shutil, "which", lambda cmd: cmd == "poetry")
    result = get_pip_packages()
    captured = capsys.readouterr()
    assert "poetry" in captured.out
    assert "poetry export" in captured.out
    assert result == []


def test_conda_fallback_message(monkeypatch, capsys):
    """
    Should print an error message if conda is found but not pip or uv
    """
    monkeypatch.setattr(shutil, "which", lambda cmd: cmd == "conda")
    result = get_pip_packages()
    captured = capsys.readouterr()
    assert "conda" in captured.out
    assert "conda list --export" in captured.out
    assert result == []


def test_nothing_found(monkeypatch, capsys):
    """
    Should print an error if no tool is found
    """
    monkeypatch.setattr(shutil, "which", lambda cmd: False)
    result = get_pip_packages()
    captured = capsys.readouterr()
    assert "No supported package manager" in captured.out
    assert result == []


def test_invalid_json(monkeypatch, capsys):
    """
    Should handle invalid JSON from subprocess
    """
    monkeypatch.setattr(shutil, "which", lambda cmd: cmd == "uv")

    def fake_run(*args, **kwargs):
        return FakeResult("not a json", 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = get_pip_packages()
    assert result == []


def test_command_fails(monkeypatch, capsys):
    """
    Test for case without a package manager
    """

    class FakeResult:
        def __init__(self):
            self.stdout = ""
            self.stderr = "Simulated error output"
            self.returncode = 1

    monkeypatch.setattr(shutil, "which", lambda cmd: True)
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: FakeResult())

    result = get_pip_packages()
    captured = capsys.readouterr()
    assert "Package manager command failed" in captured.out
    assert result == []
