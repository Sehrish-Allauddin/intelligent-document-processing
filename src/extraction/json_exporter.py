import json
from pathlib import Path


class JSONExporter:

    @staticmethod
    def save(data, output_path):

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(output_path, "w") as file:

            json.dump(
                data,
                file,
                indent=4
            )