from pathlib import Path
import json
import csv

import torch

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)


class Evaluator:

    def __init__(self, model, device, class_names):

        self.model = model
        self.device = device
        self.class_names = class_names

        Path("reports").mkdir(
            parents=True,
            exist_ok=True
        )

    def evaluate(self, dataloader):

        self.model.eval()

        y_true = []
        y_pred = []

        with torch.no_grad():

            for images, labels in dataloader:

                images = images.to(self.device)

                labels = labels.to(self.device)

                outputs = self.model(images)

                _, predicted = torch.max(outputs, 1)

                y_true.extend(
                    labels.cpu().numpy()
                )

                y_pred.extend(
                    predicted.cpu().numpy()
                )

        accuracy = accuracy_score(
            y_true,
            y_pred
        )

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        )

        report = classification_report(
            y_true,
            y_pred,
            target_names=self.class_names,
            zero_division=0,
        )

        matrix = confusion_matrix(
            y_true,
            y_pred
        )

        self.save_report(
            accuracy,
            precision,
            recall,
            f1,
            report,
        )

        self.save_metrics(
            accuracy,
            precision,
            recall,
            f1,
        )

        self.save_confusion_matrix_csv(
            matrix
        )

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    def save_report(
        self,
        accuracy,
        precision,
        recall,
        f1,
        report,
    ):

        with open(
            "reports/classification_report.txt",
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                f"Accuracy : {accuracy:.4f}\n"
            )

            file.write(
                f"Precision : {precision:.4f}\n"
            )

            file.write(
                f"Recall : {recall:.4f}\n"
            )

            file.write(
                f"F1 Score : {f1:.4f}\n\n"
            )

            file.write(report)

        print("✅ Classification Report Saved")

    def save_metrics(
        self,
        accuracy,
        precision,
        recall,
        f1,
    ):

        metrics = {

            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),

        }

        with open(
            "reports/metrics.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                metrics,
                file,
                indent=4,
            )

        print("✅ Metrics Saved")

    def save_confusion_matrix_csv(
        self,
        matrix,
    ):

        with open(
            "reports/confusion_matrix.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerows(matrix)

        print("✅ Confusion Matrix CSV Saved")