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
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional, Union

from lightning_sdk.machine import Machine
from lightning_sdk.organization import Organization
from lightning_sdk.status import Status
from lightning_sdk.studio import Studio
from lightning_sdk.teamspace import Teamspace
from lightning_sdk.user import User
from litsandbox.code_inspect import func_to_source

logger = logging.getLogger(__name__)


@dataclass
class Output:
    text: str
    exit_code: int


class Sandbox:
    """Run untrusted code safely in an isolated environment.

    Built on top of Lightning AI Studio, each Sandbox creates a dedicated cloud machine
    that automatically starts when needed and can be easily cleaned up when done.

    Example:
        >>> sandbox = Sandbox()
        >>> output = sandbox.run("pip install numpy && python -c 'import numpy; print(numpy.__version__)'")
        >>> sandbox.delete()  # Clean up when done

    Args:
        name: Optional name for the sandbox (default: auto-generated timestamp-based name)
        machine: Machine type to use (default: CPU)
        interruptible: Whether the sandbox can be interrupted (default: None)
        teamspace: Teamspace for resource allocation (default: None)
        org: Organization context for the sandbox (default: None)
        user: User context for the sandbox (default: None)
        cloud_account: Cloud account for resource billing (default: None)
        disable_secrets: If True, user secrets like LIGHTNING_API_KEY are not exposed (default: True)
    """

    def __init__(
        self,
        name: Optional[str] = None,
        machine: Optional[str] = None,
        interruptible: Optional[bool] = None,
        teamspace: Optional[Union[str, Teamspace]] = None,
        org: Optional[Union[str, Organization]] = None,
        user: Optional[Union[str, User]] = None,
        cloud_account: Optional[str] = None,
        disable_secrets: bool = True,
    ) -> None:
        if name is None:
            timestr = datetime.now().strftime("%b-%d-%H_%M")
            name = f"sandbox-{timestr}"

        self._machine = machine or Machine.CPU
        self._interruptible = interruptible

        try:
            self._studio = Studio(
                name=name,
                teamspace=teamspace,
                org=org,
                user=user,
                cloud_account=cloud_account,
                disable_secrets=disable_secrets,
            )
        except AttributeError as e:
            raise RuntimeError("Failed to create sandbox") from e

    @property
    def status(self) -> Status:
        """Returns the status of the sandbox.

        The status can be one of the following:
        - Status.NotCreated: The sandbox is not created.
        - Status.Pending: The sandbox is pending.
        - Status.Running: The sandbox is running.
        - Status.Stopping: The sandbox is stopping.
        - Status.Stopped: The sandbox is stopped.
        - Status.Completed: The sandbox is completed.
        - Status.Failed: The sandbox is failed.
        """
        return self._studio.status

    def start(self) -> None:
        """Starts the sandbox if it is not already running."""
        if self._studio.status == Status.Running:
            logger.warning("Sandbox is already running. Skipping start.", stacklevel=2)
            return

        if self._studio.status == Status.Pending:
            logger.warning("Sandbox is already starting. Skipping start.", stacklevel=2)
            return

        try:
            self._studio.start(machine=self._machine, interruptible=self._interruptible)
        except Exception as e:
            raise RuntimeError("Failed to start sandbox") from e

    def stop(self) -> None:
        """Stops the sandbox if it is not already stopped."""
        if self._studio.status == Status.NotCreated:
            raise RuntimeError("Cannot stop sandbox: it is not created.")
        self._studio.stop()

    def delete(self) -> None:
        """Permanently deletes the sandbox and all associated data.

        This operation removes all data stored on the sandbox's disk, deletes the sandbox configuration, and cannot be undone.
        Since sandboxes persist across restarts, you must explicitly call this method to clean up resources when they are no longer needed.

        Example:
            >>> sandbox = Sandbox("my-sandbox")
            >>> # ... use sandbox ...
            >>> sandbox.delete()  # Clean up when done
        """
        self._studio.delete()

    def run(self, code: str) -> Output:
        """Executes a command in the sandbox environment.

        This method automatically starts the sandbox if it's not already running.
        code is executed with sudo permissions in an isolated environment.

        Args:
            code: Python code to execute in the sandbox.

        Returns:
            Output: A dataclass containing:
                - text: The command's stdout/stderr output
                - exit_code: The command's exit status (0 for success)

        Example:
            >>> sandbox = Sandbox()
            >>> output = sandbox.run("echo 'Hello from sandbox!'")
            >>> print(output.text)
            # Hello from sandbox!
        """
        if self.status != Status.Running:
            logger.debug(
                "Sandbox.run called without starting the sandbox first. Starting it."
            )
            self.start()
        output, exit_code = self._studio.run_with_exit_code(code)
        if exit_code != 0:
            raise Exception(f"Command failed with exit code {exit_code}: {output}")
        return Output(text=output, exit_code=exit_code)

    def run_python_code(self, code: Union[str, Callable]) -> Output:
        """Runs the python code and returns the output.

        Args:
            code: The Python code string to execute

        Returns:
            Output: The result of executing the code

        Raises:
            SyntaxError: If the code has syntax errors
            ValueError: If the code is empty or only whitespace
        """
        if isinstance(code, Callable):
            code = func_to_source(code)

        command = f"python - <<EOF\n{code}\nEOF"
        return self.run(command)
