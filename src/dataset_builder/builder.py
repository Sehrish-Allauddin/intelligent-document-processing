from src.dataset_builder.config import DATASETS, OUTPUT_DATASET
from src.dataset_builder.splitter import DatasetSplitter


class DatasetBuilder:

    def __init__(self):

        self.output = OUTPUT_DATASET
        self.splitter = DatasetSplitter()

        # Dataset path -> Output class name
        self.datasets = {
            "invoice": {
                "path": DATASETS["invoice"],
                "label": "invoice"
            },
            "receipt": {
                "path": DATASETS["receipt"],
                "label": "receipt"
            },
            "resume": {
                "path": DATASETS["resumes"],
                "label": "resume"
            },
            "form": {
                "path": DATASETS["funsd"],
                "label": "form"
            },

            # Optional:
            # Uncomment if you want to use SROIE as receipt data
            # "receipt_sroie": {
            #     "path": DATASETS["sroie"],
            #     "label": "receipt"
            # },

            # Optional:
            # Uncomment later if you want RVL-CDIP as "other"
            # "other": {
            #     "path": DATASETS["rvl_cdip"],
            #     "label": "other"
            # }
        }

    def build(self):

        print("=" * 50)
        print("Building Business Document Dataset")
        print("=" * 50)

        for name, dataset in self.datasets.items():

            print(f"\nProcessing {name}")

            self.splitter.split_images(
                dataset["path"],
                self.output,
                dataset["label"]
            )

        print("\nDataset Build Complete.")