from torch.utils.data import DataLoader
import torch


def create_dataloader(
    dataset,
    batch_size=32,
    shuffle=True,
    num_workers=0
):

    return DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        persistent_workers=(num_workers > 0),
        drop_last=False
    )