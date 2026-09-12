from src.dataset.dataset_loader import DatasetLoader
from src.dataset.document_dataset import DocumentDataset
from src.dataset.transforms import get_train_transforms
from src.dataset.label_encoder import LabelEncoder

loader = DatasetLoader("datasets/rvl_cdip/RVL-CDIP")
images = loader.get_image_paths()

encoder = LabelEncoder("datasets/rvl_cdip/RVL-CDIP", split="test")

dataset = DocumentDataset(
    images,
    label_encoder=encoder,
    transform=get_train_transforms()
)

image, label = dataset[0]

print("Image Shape:", image.shape)
print("Numeric Label:", label)
print("Decoded Label:", encoder.decode(label))