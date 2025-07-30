from openai import OpenAI
from litsandbox import Sandbox


# Prompt the model to generate Python code
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful Python coding assistant. Only return clean, executable Python code with no explanations. Your response will be executed directly.",
        },
        {
            "role": "user",
            "content": "Write a Python program that prints the first 5 square numbers.",
        },
    ],
)
generated_code = response.choices[0].message.content.strip()
print("Generated Code:\n", generated_code)


# Execute the code securely in a sandbox
sandbox = Sandbox(
    machine="CPU", teamspace="sandbox", org="lightning-ai"
)  # Create a sandbox in your teamspace
output = sandbox.run_python_code(generated_code)
print("\nExecution Output:\n", output.text)
# Stop the sandbox
sandbox.stop()
sandbox.delete()
