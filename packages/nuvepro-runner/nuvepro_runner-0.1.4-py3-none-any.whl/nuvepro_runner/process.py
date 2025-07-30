import os
import subprocess

class Process:
    def __init__(self, runner):
        self.runner = runner

    def code_run(self, code: str):
        
        return self.runner.run_code(code)

    def exec(self, command: str, cwd=None, timeout=10):
        return self.runner.exec(command, cwd, timeout)


    def upload_file(self, path: str, content: bytes):
        return self.runner.upload_file(path, content)
    
    def exicutefile_code(self, path: str): 
        return self.runner.exc_file_code(path)