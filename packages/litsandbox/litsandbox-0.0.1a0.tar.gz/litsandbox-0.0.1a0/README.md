<div align='center'>

<h1> ⚡ LitSandbox </h1>

**Run AI generated code in a safe isolated environment for agents and prototypes.**

&nbsp; 
</div>

Running untrusted or AI-generated code can compromise local environments or lead to unintended side effects. LitSandbox provides a secure, disposable, and isolated environment specifically designed for executing AI generated code safely. 

Experiment safely and build prototypes without compromising security.

<div align='center'>
  
<pre>
✅ Run code in a sandbox     ✅ Integrate with MCP Server  ✅ Support GPU machine
✅ No MLOps glue code        ✅ Easy setup in Python       ✅ Install any package

</pre>
</div>

<p align="center">
  <a href="https://lightning.ai/">Lightning AI</a> •
  <a href="https://lightning.ai/docs/overview/build-agents/LitSandbox">Docs</a> •
  <a href="#quick-start">Quick start</a>
</p>


# Quick start

Install LitSandbox via pip:

```bash
pip install litsandbox
```

## Example

```python
from litsandbox import Sandbox

s = Sandbox()
output = s.run('git clone https://github.com/octocat/Hello-World.git')
s.run_python_code("f = open('file.txt', 'w'); f.write('hello world')")
s.stop()
```

# Key benefits

- Run code in a safe, isolated environment
- Data persists across restarts
- Supports GPU machines
- Integrate with MCP Server
- Easy setup in Python
- Install any package


# Build agentic system

Safely prototype with LLM-generated code using a sandboxed execution environment.

```python
from openai import OpenAI
from litsandbox import Sandbox


# Prompt the model to generate Python code
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": "You are a helpful Python coding assistant. Only return clean, executable Python code with no explanations. Your response will be executed directly."},
        {"role": "user", "content": "Write a Python program that prints the first 5 square numbers."}
])
generated_code = response.choices[0].message.content.strip()
print("Generated Code:\n", generated_code)


# Execute the code securely in a sandbox
sandbox = Sandbox(machine="CPU")
output = sandbox.run_python_code(generated_code)
print("\nExecution Output:\n", output.text)
# Stop the sandbox
sandbox.stop()
```
