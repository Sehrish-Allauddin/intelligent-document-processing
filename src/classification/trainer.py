from pathlib import Path
from torch.optim.lr_scheduler import CosineAnnealingLR
import torch
import torch.nn as nn
from torch.optim import AdamW
from tqdm import tqdm


class Trainer:

    def __init__(
        self,
        model,
        train_loader,
        valid_loader,
        device,
        learning_rate=1e-4,
        model_save_path="models/best_model.pth",

    ):
       
        self.model = model
        self.train_loader = train_loader
        self.valid_loader = valid_loader
        self.device = device
        self.patience = 5

        self.counter = 0
        self.criterion = nn.CrossEntropyLoss()

        self.optimizer = AdamW(
            self.model.parameters(),
            lr=learning_rate
        )
    
        self.scheduler = CosineAnnealingLR(
            self.optimizer,
            T_max=20
        )

        self.best_accuracy = 0

        self.model_save_path = Path(model_save_path)
        self.model_save_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def train_one_epoch(self):

        self.model.train()

        running_loss = 0.0
        correct = 0
        total = 0

        progress = tqdm(
            self.train_loader,
            desc="Training",
            leave=False
        )

        for images, labels in progress:

            images = images.to(self.device)
            labels = labels.to(self.device)

            self.optimizer.zero_grad()

            outputs = self.model(images)

            loss = self.criterion(outputs, labels)

            loss.backward()

            self.optimizer.step()

            running_loss += loss.item()

            _, predicted = outputs.max(1)

            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            progress.set_postfix(
                loss=f"{loss.item():.4f}",
                acc=f"{100 * correct / total:.2f}%"
            )

        avg_loss = running_loss / len(self.train_loader)
        accuracy = 100 * correct / total

        return avg_loss, accuracy

    def validate_one_epoch(self):

        self.model.eval()

        running_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():

            for images, labels in self.valid_loader:

                images = images.to(self.device)
                labels = labels.to(self.device)

                outputs = self.model(images)

                loss = self.criterion(outputs, labels)

                running_loss += loss.item()

                _, predicted = outputs.max(1)

                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

        avg_loss = running_loss / len(self.valid_loader)
        accuracy = 100 * correct / total

        return avg_loss, accuracy

    def save_best_model(self, validation_accuracy):

      if validation_accuracy > self.best_accuracy:

        self.best_accuracy = validation_accuracy

        self.counter = 0

        torch.save(
            self.model.state_dict(),
            self.model_save_path
        )

        print("✅ Best model saved.")

      else:

        self.counter += 1


    def early_stop(self):

      return self.counter >= self.patience

    print("✅ Best model saved.")