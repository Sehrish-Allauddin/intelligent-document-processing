import albumentations as A
from albumentations.pytorch import ToTensorV2


IMAGE_SIZE = 224


train_transform = A.Compose([
    A.Resize(IMAGE_SIZE, IMAGE_SIZE),

    A.HorizontalFlip(p=0.5),

    A.Rotate(limit=10, p=0.5),

    A.RandomBrightnessContrast(p=0.3),

    A.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    ),

    ToTensorV2()
])


valid_transform = A.Compose([
    A.Resize(IMAGE_SIZE, IMAGE_SIZE),

    A.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    ),

    ToTensorV2()
])


test_transform = valid_transform