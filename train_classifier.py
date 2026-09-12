import torch

from src.classification.dataloader import DocumentDataLoader
from src.classification.model import DocumentClassifier
from src.classification.trainer import Trainer
from src.classification.evaluator import Evaluator
# -------------------------------------
# Configuration
# -------------------------------------

BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 1e-4

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 60)
print("Business Document Classifier")
print("=" * 60)
print(f"Using Device : {DEVICE}")

# -------------------------------------
# Data
# -------------------------------------

data = DocumentDataLoader(
    batch_size=BATCH_SIZE,
    num_workers=0
)

print(f"Classes : {data.classes}")
print(f"Number of Classes : {data.num_classes}")

# -------------------------------------
# Model
# -------------------------------------

model = DocumentClassifier(
    num_classes=data.num_classes
).to(DEVICE)

# -------------------------------------
# Trainer
# -------------------------------------

trainer = Trainer(
    model=model,
    train_loader=data.train_loader,
    valid_loader=data.valid_loader,
    device=DEVICE,
    learning_rate=LEARNING_RATE,
)

# -------------------------------------
# Training Loop
# -------------------------------------

for epoch in range(EPOCHS):

    print(f"\nEpoch {epoch + 1}/{EPOCHS}")
    print("-" * 50)

    train_loss, train_acc = trainer.train_one_epoch()

    val_loss, val_acc = trainer.validate_one_epoch()

    print(f"Train Loss : {train_loss:.4f}")
    print(f"Train Acc  : {train_acc:.2f}%")

    print(f"Val Loss   : {val_loss:.4f}")
    print(f"Val Acc    : {val_acc:.2f}%")

    trainer.save_best_model(val_acc)

    current_lr = trainer.optimizer.param_groups[0]["lr"]

    print(f"Learning Rate : {current_lr:.8f}")

model.load_state_dict(
    torch.load("models/best_model.pth")
)

evaluator = Evaluator(
    model=model,
    device=DEVICE,
    class_names=data.classes,
)

metrics = evaluator.evaluate(
    data.test_loader
)

print("\nFinal Test Metrics")

for key, value in metrics.items():

    print(f"{key.title()} : {value:.4f}")
    
print("\nTraining Complete!")