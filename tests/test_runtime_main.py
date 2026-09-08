import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("runtime_main", ROOT / "06_RUNTIME" / "core" / "runtime_main.py")
runtime_main = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime_main)


def _result(stdout="", returncode=0, stderr=""):
    return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=returncode)


def test_git_pull_does_not_pop_an_unrelated_stash_when_clean():
    runtime_main.log = Mock()
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        if args[:3] == ["git", "status", "--porcelain"]:
            return _result()
        return _result()

    with patch.object(runtime_main.subprocess, "run", side_effect=run):
        assert runtime_main.git_pull() is True

    assert ["git", "stash", "pop"] not in calls


def test_git_pull_restores_only_the_stash_it_created():
    runtime_main.log = Mock()
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        if args[:3] == ["git", "status", "--porcelain"]:
            return _result(" M notes.md\n")
        if args[:3] == ["git", "stash", "push"]:
            return _result("Saved working directory and index state")
        return _result()

    with patch.object(runtime_main.subprocess, "run", side_effect=run):
        assert runtime_main.git_pull() is True

    assert ["git", "stash", "pop"] in calls


def test_git_pull_keeps_stash_when_pull_fails():
    runtime_main.log = Mock()
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        if args[:3] == ["git", "status", "--porcelain"]:
            return _result(" M notes.md\n")
        if args[:3] == ["git", "stash", "push"]:
            return _result("Saved working directory and index state")
        if args[:3] == ["git", "pull", "--rebase"]:
            return _result(returncode=1, stderr="network error")
        return _result()

    with patch.object(runtime_main.subprocess, "run", side_effect=run):
        assert runtime_main.git_pull() is False

    assert ["git", "stash", "pop"] not in calls


def test_git_pull_reports_restore_exception_without_masking_pull_success():
    runtime_main.log = Mock()

    def run(args, **kwargs):
        if args[:3] == ["git", "status", "--porcelain"]:
            return _result(" M notes.md\n")
        if args[:3] == ["git", "stash", "push"]:
            return _result("Saved working directory and index state")
        if args == ["git", "stash", "pop"]:
            raise TimeoutError("restore timed out")
        return _result()

    with patch.object(runtime_main.subprocess, "run", side_effect=run):
        assert runtime_main.git_pull() is True

    runtime_main.log.error.assert_called_once()


def test_detect_new_reports_uses_relative_path_to_avoid_name_collisions(tmp_path):
    cloud = tmp_path / "cloud"
    (cloud / "advisor").mkdir(parents=True)
    (cloud / "signals").mkdir(parents=True)
    (cloud / "advisor" / "report.md").write_text("a")
    (cloud / "signals" / "report.md").write_text("b")
    runtime_main.CLOUD_DIR = cloud

    reports = runtime_main.detect_new_reports({"advisor/report.md"})

    assert [p.relative_to(cloud).as_posix() for p in reports] == ["signals/report.md"]


def test_save_pushed_files_replaces_state_atomically(tmp_path):
    runtime_main.PUSHED_FILES = tmp_path / "tg_pushed.json"
    runtime_main.PUSHED_FILES.write_text('["old/report.md"]', encoding="utf-8")

    runtime_main.save_pushed_files({"signals/z.md", "advisor/a.md"})

    assert runtime_main.PUSHED_FILES.read_text(encoding="utf-8") == (
        '["advisor/a.md", "signals/z.md"]'
    )
    assert not (tmp_path / "tg_pushed.json.tmp").exists()
