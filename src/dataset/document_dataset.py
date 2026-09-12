from PIL import Image
from torch.utils.data import Dataset


class DocumentDataset(Dataset):

    def __init__(self, image_paths, label_encoder, transform=None):

        self.image_paths = image_paths
        self.label_encoder = label_encoder
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):

        image_path = self.image_paths[idx]

        image = Image.open(image_path).convert("RGB")

        label_name = image_path.parent.name
        label = self.label_encoder.encode(label_name)

        if self.transform:
            image = self.transform(image)

        return image, label