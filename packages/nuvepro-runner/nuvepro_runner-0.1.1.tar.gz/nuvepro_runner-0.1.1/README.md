# Nuvepro Runner

A Python SDK to run code in a secure, sandboxed local workspace.

## Features

- Run dynamic Python code
- Execute shell commands
- Upload temporary files
- Clean up sandbox environments

## Example

```python
from nuvepro_runner import Nuvepro

sandbox = Nuvepro().create()
response = sandbox.process.code_run('print("Hello from Nuvepro!")')
print(response["output"])
sandbox.cleanup()
