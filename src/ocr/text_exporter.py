from pathlib import Path
import json
import numpy as np


class TextExporter:

    @staticmethod
    def save_txt(text, output_path):

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(text)

        print("✅ OCR Text Saved")

    @staticmethod
    def convert_numpy(obj):

        if isinstance(obj, np.integer):
            return int(obj)

        if isinstance(obj, np.floating):
            return float(obj)

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        raise TypeError(
            f"{type(obj)} is not JSON serializable"
        )

    @staticmethod
    def save_json(data, output_path):

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
                default=TextExporter.convert_numpy
            )

        print("✅ OCR JSON Saved")