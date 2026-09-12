from torchvision import transforms


def get_train_transforms():

    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(5),
        transforms.RandomHorizontalFlip(0.5),
        transforms.ToTensor(),
    ])


def get_test_transforms():

    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])