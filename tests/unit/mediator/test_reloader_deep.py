import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from nexelpy.mediator.reloader import Reloader


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    entry = tmp_path / "main.py"
    entry.write_text("print('x')")
    return entry


def _fake_child(pid=100, poll_value=None):
    child = MagicMock()
    child.pid = pid
    child.poll.return_value = poll_value
    child.wait.return_value = 0
    child.returncode = 0
    return child


def _interrupting_sleep(n_to_raise=1):
    state = {"n": 0}

    def fake_sleep(_):
        state["n"] += 1
        if state["n"] >= n_to_raise:
            raise KeyboardInterrupt

    return fake_sleep


def _fake_spawn_with_ready(ready_path):
    def _spawn(self):
        self._ready_file = ready_path
        self._child_ready = False
        self._spawn_time = 0
        ready_path.write_text("ready")
        return _fake_child()

    return _spawn


def _fake_spawn_no_ready(ready_path):
    def _spawn(self):
        self._ready_file = ready_path
        self._child_ready = False
        self._spawn_time = 0
        return _fake_child()

    return _spawn


def test_iter_files_yields_only_matching_exts(project):
    (project.parent / "other.py").touch()
    (project.parent / "note.txt").touch()
    r = Reloader(entry_file=str(project))
    files = list(r._iter_files())
    assert any(str(f).endswith(".py") for f in files)
    assert not any(str(f).endswith(".txt") for f in files)


def test_iter_files_skips_ignored_dirs(project):
    cache = project.parent / "__pycache__"
    cache.mkdir()
    (cache / "x.py").touch()
    r = Reloader(entry_file=str(project))
    files = list(r._iter_files())
    assert not any("__pycache__" in str(f) for f in files)


def test_iter_files_includes_extra_ignore_dirs(project):
    extra = project.parent / "custom"
    extra.mkdir()
    (extra / "x.py").touch()
    r = Reloader(entry_file=str(project), extra_ignore_dirs=["custom"])
    files = list(r._iter_files())
    assert not any("custom" in str(f) for f in files)


def test_iter_files_custom_exts(project):
    (project.parent / "script.js").touch()
    r = Reloader(entry_file=str(project), exts=(".js",))
    files = list(r._iter_files())
    assert all(str(f).endswith(".js") for f in files)


def test_spawn_child_sets_env_and_returns_popen(project):
    fake = _fake_child()

    with patch(
        "nexelpy.mediator.reloader.subprocess.Popen", return_value=fake
    ) as mock_popen:
        r = Reloader(entry_file=str(project))
        child = r._spawn_child()

        assert child is fake
        args, kwargs = mock_popen.call_args
        assert kwargs["env"][Reloader.CHILD_ENV_KEY] == "1"
        assert kwargs["env"][Reloader.READY_ENV_KEY] == str(r._ready_file)
        assert str(project) in args[0]


def test_spawn_child_sets_ready_file_attribute(project):
    fake = _fake_child()
    with patch("nexelpy.mediator.reloader.subprocess.Popen", return_value=fake):
        r = Reloader(entry_file=str(project))
        r._spawn_child()
        assert r._ready_file is not None
        assert "nexelpy_ready" in r._ready_file.name


def test_spawn_child_unlinks_existing_ready_file(project):
    fake = _fake_child()
    existing = Path("/tmp/nexelpy_ready_test_stale")
    existing.write_text("stale")
    try:
        with patch("nexelpy.mediator.reloader.subprocess.Popen", return_value=fake), \
             patch.object(Reloader, "_make_ready_path", return_value=existing):
            r = Reloader(entry_file=str(project))
            r._spawn_child()
            assert not existing.exists()
    finally:
        existing.unlink(missing_ok=True)


def test_stop_child_none_does_nothing(project):
    r = Reloader(entry_file=str(project))
    r._child = None
    r._stop_child()


def test_stop_child_already_exited(project):
    r = Reloader(entry_file=str(project))
    child = MagicMock()
    child.poll.return_value = 0
    r._child = child
    r._stop_child()
    child.terminate.assert_not_called()
    assert r._child is None


def test_stop_child_sends_terminate(project):
    r = Reloader(entry_file=str(project))
    child = MagicMock()
    child.poll.side_effect = [None, None, 0, 0, 0]
    r._child = child

    with patch("nexelpy.mediator.reloader.time.sleep"):
        r._stop_child()
        child.terminate.assert_called_once()


def test_stop_child_force_kills_on_timeout(project):
    r = Reloader(entry_file=str(project))
    child = MagicMock()
    child.poll.return_value = None
    r._child = child

    with patch("nexelpy.mediator.reloader.time.sleep"):
        r._stop_child(timeout=0.0)
        child.terminate.assert_called_once()
        child.kill.assert_called_once()


def test_stop_child_unlinks_ready_file(project):
    r = Reloader(entry_file=str(project))
    ready = project.parent / "ready.marker"
    ready.write_text("x")
    r._ready_file = ready

    child = MagicMock()
    child.poll.return_value = 0
    r._child = child
    r._stop_child()
    assert not ready.exists()


def test_restart_respects_cooldown(project):
    r = Reloader(entry_file=str(project), reload_cooldown=100.0)
    r._last_reload = time.time()
    r._child = _fake_child()

    with patch("nexelpy.mediator.reloader.time.time", return_value=r._last_reload + 1):
        with patch.object(Reloader, "_spawn_child") as mock_spawn, \
             patch.object(Reloader, "_stop_child") as mock_stop:
            r._restart("test")
            mock_stop.assert_not_called()
            mock_spawn.assert_not_called()
            assert r._pending_change_at is not None


def test_restart_after_cooldown(project):
    r = Reloader(entry_file=str(project), reload_cooldown=0.0)
    r._last_reload = 0

    with patch("nexelpy.mediator.reloader.time.time", return_value=1000), \
         patch.object(Reloader, "_stop_child") as mock_stop, \
         patch.object(Reloader, "_spawn_child", return_value=_fake_child(pid=999)) as mock_spawn:
        r._restart("change")
        mock_stop.assert_called_once()
        mock_spawn.assert_called_once()
        assert r._child.pid == 999


def test_run_breaks_on_nonzero_exit(project):
    fake = _fake_child(poll_value=1)
    fake.returncode = 1

    with patch("nexelpy.mediator.reloader.subprocess.Popen", return_value=fake), \
         patch("nexelpy.mediator.reloader.time.sleep"), \
         patch("nexelpy.mediator.reloader.time.time", return_value=0), \
         patch("nexelpy.mediator.reloader.console.print"):
        r = Reloader(entry_file=str(project))
        r.run()

    assert fake.terminate.called or fake.poll.called


def test_run_breaks_on_normal_exit(project):
    fake = _fake_child(poll_value=0)
    fake.returncode = 0

    with patch("nexelpy.mediator.reloader.subprocess.Popen", return_value=fake), \
         patch("nexelpy.mediator.reloader.time.sleep"), \
         patch("nexelpy.mediator.reloader.time.time", return_value=0):
        r = Reloader(entry_file=str(project))
        r.run()


def test_run_waits_for_ready_file(project):
    ready = project.parent / "ready.marker"

    with patch.object(Reloader, "_spawn_child", _fake_spawn_with_ready(ready)), \
         patch("nexelpy.mediator.reloader.time.sleep", side_effect=_interrupting_sleep(2)), \
         patch("nexelpy.mediator.reloader.time.time", return_value=0):
        r = Reloader(entry_file=str(project))
        with pytest.raises(KeyboardInterrupt):
            r.run()

    assert r._child_ready is True


def test_run_ready_timeout(project):
    with patch.object(Reloader, "_spawn_child", _fake_spawn_no_ready(Path("/tmp/never_exists"))), \
         patch.object(Reloader, "_snapshot", return_value={"main.py": 100}), \
         patch("nexelpy.mediator.reloader.time.sleep", side_effect=_interrupting_sleep(2)), \
         patch("nexelpy.mediator.reloader.time.time", return_value=200):
        r = Reloader(entry_file=str(project), ready_timeout=1.0)
        with pytest.raises(KeyboardInterrupt):
            r.run()

    assert r._child_ready is True


def test_run_detects_change_and_restarts(project):
    ready = project.parent / "ready.marker"

    snapshots = iter([
        {"main.py": 100},
        {"main.py": 100},
        {"main.py": 999},
        {"main.py": 999},
        {"main.py": 999},
    ])

    def fake_snapshot(self):
        return next(snapshots, {"main.py": 999})

    sleep_count = {"n": 0}
    def fake_sleep(_):
        sleep_count["n"] += 1
        if sleep_count["n"] >= 3:
            raise KeyboardInterrupt

    with patch.object(Reloader, "_spawn_child", _fake_spawn_with_ready(ready)), \
         patch.object(Reloader, "_snapshot", fake_snapshot), \
         patch.object(Reloader, "_restart") as mock_restart, \
         patch("nexelpy.mediator.reloader.time.sleep", side_effect=fake_sleep), \
         patch("nexelpy.mediator.reloader.time.time", return_value=1000):
        r = Reloader(entry_file=str(project), settle_window=0.0)
        with pytest.raises(KeyboardInterrupt):
            r.run()
        assert mock_restart.called

def test_run_keyboard_interrupt_stops_child(project):
    fake = _fake_child()
    ready = project.parent / "ready.marker"
    ready.write_text("x")

    with patch("nexelpy.mediator.reloader.subprocess.Popen", return_value=fake), \
         patch.object(Reloader, "_make_ready_path", return_value=ready), \
         patch.object(Reloader, "_snapshot", return_value={}), \
         patch("nexelpy.mediator.reloader.time.sleep", side_effect=KeyboardInterrupt), \
         patch("nexelpy.mediator.reloader.time.time", return_value=0):
        r = Reloader(entry_file=str(project))
        with pytest.raises(KeyboardInterrupt):
            r.run()

    assert fake.terminate.called or fake.poll.called


def test_child_env_key_value():
    assert Reloader.CHILD_ENV_KEY == "MAINAPP_CHILD"


def test_ready_env_key_value():
    assert Reloader.READY_ENV_KEY == "NEXELPY_READY_FILE"


def test_is_child_reads_MAINAPP_CHILD(monkeypatch):
    monkeypatch.setenv("MAINAPP_CHILD", "1")
    assert Reloader.is_child() is True
    monkeypatch.setenv("MAINAPP_CHILD", "0")
    assert Reloader.is_child() is False
    monkeypatch.delenv("MAINAPP_CHILD")
    assert Reloader.is_child() is False
