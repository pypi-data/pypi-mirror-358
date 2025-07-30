import litserve as ls
from litserve.mcp import MCP
from litserve.server import HTTPException
from litsandbox import Sandbox


class CodeExecutor(ls.LitAPI):
    def setup(self, device):
        # Create a sandbox in your teamspace
        self.sandbox = Sandbox(teamspace="sandbox", org="lightning-ai")

    def predict(self, request: dict) -> str:
        if not isinstance(request, dict) or "code" not in request:
            raise HTTPException(status_code=400, detail="Code is required")

        try:
            output = self.sandbox.run(request["code"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error executing code: {e}")

        if output.exit_code != 0:
            raise HTTPException(
                status_code=500, detail=f"Error executing code: {output.text}"
            )

        return output.text


if __name__ == "__main__":
    api = CodeExecutor(
        mcp=MCP(
            name="code-executor",
            description="Execute code in a sandbox. {'code': 'CODE_TO_EXECUTE'}",
        )
    )
    server = ls.LitServer(api)
    server.run()

    # Delete the sandbox
    sandbox = Sandbox(teamspace="sandbox", org="lightning-ai")
    sandbox.delete()
