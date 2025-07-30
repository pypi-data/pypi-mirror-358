# Copyright The Lightning AI team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
from unittest.mock import patch
from lightning_sdk.machine import Machine
from lightning_sdk.status import Status

import pytest

from litsandbox import Sandbox, Output


@patch("litsandbox.sandbox.Studio")
def test_sandbox(mock_studio):
    mock_studio.return_value.run_with_exit_code.return_value = ("Python 3.10.0", 0)
    sandbox = Sandbox(teamspace="growth", org="lightning-ai")
    sandbox.start()
    output = sandbox.run("python --version")
    assert output.text == "Python 3.10.0"
    assert output.exit_code == 0
    sandbox.stop()


@patch("litsandbox.sandbox.Studio")
def test_run(mock_studio, caplog):
    mock_studio.return_value.status = Status.NotCreated
    mock_studio.return_value.run_with_exit_code.return_value = ("3.12.0", 0)
    s = Sandbox(teamspace="test", org="test")
    with caplog.at_level(logging.DEBUG):
        s.run("python --version")

    mock_studio.return_value.start.assert_called_once_with(
        machine=Machine.CPU, interruptible=None
    )
    assert "called without starting the sandbox first" in caplog.text


@patch("litsandbox.sandbox.Studio")
def test_run_error_output(mock_studio, caplog):
    mock_studio.return_value.status = Status.NotCreated
    mock_studio.return_value.run_with_exit_code.return_value = ("", -1)
    s = Sandbox(teamspace="test", org="test")
    with pytest.raises(Exception, match="Command failed with exit code -1"):
        s.run("python --version")


@patch("litsandbox.sandbox.Studio")
@patch("litsandbox.Sandbox.run", return_value=Output(text="hello world", exit_code=0))
def test_run_python_code(mock_run, mock_studio):
    sandbox = Sandbox(teamspace="growth", org="lightning-ai")
    sandbox.start()
    output = sandbox.run_python_code("print('hello world')")
    assert output.text == "hello world"
    assert output.exit_code == 0
    sandbox.stop()


@patch("litsandbox.sandbox.Studio")
def test_start(mock_studio):
    mock_studio.return_value.status = Status.NotCreated
    sandbox = Sandbox(teamspace="growth", org="lightning-ai")
    sandbox.start()
    mock_studio.return_value.start.assert_called_once_with(
        machine=Machine.CPU, interruptible=None
    )


@patch("litsandbox.sandbox.Studio")
def test_start_already_running(mock_studio, caplog):
    mock_studio.return_value.status = Status.Running
    sandbox = Sandbox(teamspace="growth", org="lightning-ai")
    with caplog.at_level(logging.WARNING):
        sandbox.start()
    assert "already running." in caplog.text


@patch("litsandbox.sandbox.Studio")
def test_start_pending(mock_studio, caplog):
    mock_studio.return_value.status = Status.Pending
    sandbox = Sandbox(teamspace="growth", org="lightning-ai")
    with caplog.at_level(logging.WARNING):
        sandbox.start()
    assert "already starting." in caplog.text


@patch("litsandbox.sandbox.Studio")
def test_stop_not_created(mock_studio):
    mock_studio.return_value.status = Status.NotCreated
    sandbox = Sandbox(teamspace="growth", org="lightning-ai")
    with pytest.raises(RuntimeError, match="not created."):
        sandbox.stop()


@patch("litsandbox.sandbox.Studio")
def test_machine_parameter(mock_studio):
    mock_studio.return_value.status = Status.NotCreated
    sandbox = Sandbox(machine="CPU")
    sandbox.start()
    mock_studio.return_value.start.assert_called_once_with(
        machine="CPU", interruptible=None
    )
