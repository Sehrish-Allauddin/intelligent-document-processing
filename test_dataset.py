from src.dataset.dataset_loader import DatasetLoader

loader = DatasetLoader("datasets/rvl_cdip/RVL-CDIP")

images = loader.summary()

print(images[:5])