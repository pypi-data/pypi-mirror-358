import os

class FileSystem:
    def __init__(self, runner):
        self.runner = runner

    def upload_file(self, target_path: str, content: bytes):
        full_path = os.path.join(self.runner.workspace_dir, target_path.strip("/\\"))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(content)
