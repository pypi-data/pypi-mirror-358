from .runner import NuveproRunner
from .process import Process
from .fs import FileSystem

class Sandbox:
    def __init__(self,config):
        self.runner = NuveproRunner(config)
        self.process = Process(self.runner)
        self.fs = FileSystem(self.runner)

    def cleanup(self):
        self.runner.cleanup()
