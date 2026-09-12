import shutil
from pathlib import Path


class TempManager:

    def __init__(self):

        self.temp_dir = Path("temp")

    def create(self):

        self.temp_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        return self.temp_dir

    def clear(self):

        if self.temp_dir.exists():

            shutil.rmtree(self.temp_dir)

        self.temp_dir.mkdir()