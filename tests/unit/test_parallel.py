import os
import subprocess
from unittest import mock

import pytest

from testui.support import parallel


def test_process_writes_real_exit_codes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(parallel, "__set_fails_file", lambda *args: None)
    args = mock.Mock(s=False, general_markers="", general="", testrail_pwd=None)
    with mock.patch.object(
        subprocess,
        "run",
        side_effect=[mock.Mock(returncode=0), mock.Mock(returncode=5)],
    ):
        getattr(parallel, "__process")(["a", "b"], args)
    assert (tmp_path / "fails.txt").read_text() == "0\n5\n"


@pytest.mark.parametrize(
    "output",
    [
        # pytest-testrail 2.x
        '[testrail] New testrun created with name "run" and ID=7\n',
        # pytest-testrail 3.x, through --log-cli-level=INFO
        "INFO  setup ID=1 seen first\n"
        "INFO     pytest_testrail.plugin:plugin.py:524 "
        'New testrun created with name "run" and ID=7\n',
    ],
)
def test_start_run_id(output):
    args = mock.Mock(
        markers=["a", "b"],
        general_markers="",
        single_thread_marker=None,
        testrail_pwd=None,
    )
    with (
        mock.patch.object(subprocess, "Popen") as popen,
        mock.patch("builtins.open", mock.mock_open(read_data=output)),
        mock.patch.object(os, "remove"),
    ):
        assert getattr(parallel, "__start_run_id")(args, "run") == "7"
    command = popen.call_args[0][0]
    assert command[2] == "a  or b " and "--log-cli-level=INFO" in command


def test_remove_logs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for path in [
        "logs/appium_logs/a.log",
        "logs/report_screenshots/b.png",
        "logs/x.txt",
        "logs/sub/keep.txt",
    ]:
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text("x")
    parallel.remove_logs()
    left = sorted(
        str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file()
    )
    assert left == [os.path.join("logs", "sub", "keep.txt")]


def test_leftover_result_files_are_removed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for leftover in ("fails.txt", "report_fails.txt", "report_cases.txt"):
        (tmp_path / leftover).write_text("1\n")
    args = mock.Mock(testrail_id=None, testrail=None)
    monkeypatch.setattr(parallel, "__arg_parser", lambda: args)
    stop = mock.Mock(side_effect=RuntimeError("stop after clean-up"))
    monkeypatch.setattr(parallel, "get_total_number_of_cases", stop)
    with pytest.raises(RuntimeError, match="stop after clean-up"):
        parallel.parallel_testui()
    assert not list(tmp_path.glob("*.txt"))
