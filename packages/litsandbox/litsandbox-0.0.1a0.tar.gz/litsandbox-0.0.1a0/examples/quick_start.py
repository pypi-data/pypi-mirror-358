from litsandbox import Sandbox

# Start the Sandbox in your teamspace and org
sandbox = Sandbox(name="quick-start", teamspace="sandbox", org="lightning-ai")
sandbox.start()


# Install a package in the sandbox
sandbox.run("pip install numpy")

# Run a code string in a sandbox
sandbox.run_python_code("print('Hello, world!')")


# Run a function in a sandbox
def fn():
    import numpy as np

    print(np.__version__)


# Run a function in a sandbox
output = sandbox.run_python_code(fn)
print(output)

# Stop the Sandbox
sandbox.stop()

# Resume the Sandbox from a persistent state
sandbox = Sandbox(name="quick-start", teamspace="sandbox", org="lightning-ai")
sandbox.run("pip list | grep numpy")
sandbox.stop()
