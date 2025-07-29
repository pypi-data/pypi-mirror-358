import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
from tqdm import tqdm

from ...core.interfaces import AuditOps, PenaltyOps
from ...plugins.registry import register


@register('audit_ops', 'classification')
class ClassificationAuditOps(AuditOps):
    """Classification evaluation and metrics computation."""

    def __init__(self, metrics: List[str] = None, **kwargs):
        self.metrics = metrics or ['accuracy', 'precision', 'recall', 'f1']
        self.supported_metrics = [
            'accuracy', 'precision', 'recall', 'f1', 
            'confusion_matrix', 'classification_report'
        ]

        # Validate metrics
        for metric in self.metrics:
            if metric not in self.supported_metrics:
                raise ValueError(f"Unsupported metric: {metric}. "
                               f"Supported: {self.supported_metrics}")

    def evaluate(self, model: nn.Module, data_loader: DataLoader, 
                 penalty_ops: PenaltyOps, device: str, **kwargs) -> Dict[str, Any]:
        """Evaluate model on given data loader."""
        model.eval()

        all_predictions = []
        all_targets = []
        total_loss = 0.0

        print("Evaluating model...")

        with torch.no_grad():
            eval_pbar = tqdm(data_loader, desc="Evaluation")
            for batch in eval_pbar:
                data, targets = batch
                data, targets = data.to(device), targets.to(device)

                outputs = model(data)
                loss = penalty_ops.compute_loss(outputs, targets)

                total_loss += loss.item()

                # Get predictions
                _, predicted = torch.max(outputs.data, 1)

                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(targets.cpu().numpy())

        # Convert to numpy arrays
        predictions = np.array(all_predictions)
        targets = np.array(all_targets)

        # Compute metrics
        results = {
            'loss': total_loss / len(data_loader),
            'num_samples': len(targets)
        }

        # Accuracy
        if 'accuracy' in self.metrics:
            accuracy = accuracy_score(targets, predictions) * 100
            results['accuracy'] = accuracy

        # Precision
        if 'precision' in self.metrics:
            precision = precision_score(targets, predictions, average='weighted', zero_division=0) * 100
            results['precision'] = precision

        # Recall
        if 'recall' in self.metrics:
            recall = recall_score(targets, predictions, average='weighted', zero_division=0) * 100
            results['recall'] = recall

        # F1-score
        if 'f1' in self.metrics:
            f1 = f1_score(targets, predictions, average='weighted', zero_division=0) * 100
            results['f1'] = f1

        # Confusion matrix
        if 'confusion_matrix' in self.metrics:
            cm = confusion_matrix(targets, predictions)
            results['confusion_matrix'] = cm.tolist()

        # Classification report
        if 'classification_report' in self.metrics:
            report = classification_report(targets, predictions, output_dict=True, zero_division=0)
            results['classification_report'] = report

        return results

    def get_config(self) -> Dict[str, Any]:
        """Return configuration."""
        return {'metrics': self.metrics}


@register('audit_ops', 'distillation')
class DistillationAuditOps(AuditOps):
    """Distillation-specific evaluation with teacher-student metrics."""

    def __init__(self, metrics: List[str] = None, compute_agreement: bool = True, **kwargs):
        self.metrics = metrics or ['accuracy', 'precision', 'recall', 'f1']
        self.compute_agreement = compute_agreement
        self.supported_metrics = [
            'accuracy', 'precision', 'recall', 'f1',
            'confusion_matrix', 'classification_report'
        ]

        # Validate metrics
        for metric in self.metrics:
            if metric not in self.supported_metrics:
                raise ValueError(f"Unsupported metric: {metric}. "
                               f"Supported: {self.supported_metrics}")

    def evaluate(self, model: nn.Module, data_loader: DataLoader,
                 penalty_ops: PenaltyOps, device: str,
                 teacher_model: Optional[nn.Module] = None, **kwargs) -> Dict[str, Any]:
        """Evaluate student model with optional teacher comparison."""
        model.eval()

        student_predictions = []
        teacher_predictions = []
        all_targets = []
        total_loss = 0.0

        print("Evaluating distillation model...")

        with torch.no_grad():
            eval_pbar = tqdm(data_loader, desc="Distillation Evaluation")
            for batch in eval_pbar:
                data, targets = batch
                data, targets = data.to(device), targets.to(device)

                # Teacher predictions (if available)
                if teacher_model is not None:
                    teacher_model.eval()
                    teacher_outputs = teacher_model(data)
                    _, teacher_pred = torch.max(teacher_outputs.data, 1)
                    teacher_predictions.extend(teacher_pred.cpu().numpy())

                # Student predictions
                student_outputs = model(data)
                loss = penalty_ops.compute_loss(student_outputs, targets, teacher_outputs=teacher_outputs)
                total_loss += loss.item()

                _, student_pred = torch.max(student_outputs.data, 1)
                student_predictions.extend(student_pred.cpu().numpy())

                all_targets.extend(targets.cpu().numpy())

        # Convert to numpy arrays
        student_preds = np.array(student_predictions)
        targets = np.array(all_targets)

        # Compute student metrics
        results = {
            'loss': total_loss / len(data_loader),
            'num_samples': len(targets)
        }

        # Student metrics
        if 'accuracy' in self.metrics:
            student_accuracy = accuracy_score(targets, student_preds) * 100
            results['student_accuracy'] = student_accuracy
            results['accuracy'] = student_accuracy  # For compatibility

        if 'precision' in self.metrics:
            student_precision = precision_score(targets, student_preds, average='weighted', zero_division=0) * 100
            results['student_precision'] = student_precision
            results['precision'] = student_precision  # For compatibility

        if 'recall' in self.metrics:
            student_recall = recall_score(targets, student_preds, average='weighted', zero_division=0) * 100
            results['student_recall'] = student_recall
            results['recall'] = student_recall  # For compatibility

        if 'f1' in self.metrics:
            student_f1 = f1_score(targets, student_preds, average='weighted', zero_division=0) * 100
            results['student_f1'] = student_f1
            results['f1'] = student_f1  # For compatibility

        # Teacher metrics and agreement (if teacher available)
        if teacher_model is not None and teacher_predictions:
            teacher_preds = np.array(teacher_predictions)

            # Teacher accuracy
            teacher_accuracy = accuracy_score(targets, teacher_preds) * 100
            results['teacher_accuracy'] = teacher_accuracy

            # Teacher-student agreement
            if self.compute_agreement:
                agreement = accuracy_score(teacher_preds, student_preds) * 100
                results['agreement'] = agreement

                # Agreement on correct predictions
                correct_teacher = teacher_preds == targets
                correct_student = student_preds == targets
                both_correct = correct_teacher & correct_student

                if correct_teacher.sum() > 0:
                    agreement_on_correct = both_correct.sum() / correct_teacher.sum() * 100
                    results['agreement_on_correct'] = agreement_on_correct

        # Confusion matrix
        if 'confusion_matrix' in self.metrics:
            student_cm = confusion_matrix(targets, student_preds)
            results['student_confusion_matrix'] = student_cm.tolist()
            results['confusion_matrix'] = student_cm.tolist()  # For compatibility

        # Classification report
        if 'classification_report' in self.metrics:
            student_report = classification_report(targets, student_preds, output_dict=True, zero_division=0)
            results['student_classification_report'] = student_report
            results['classification_report'] = student_report  # For compatibility

        return results

    def get_config(self) -> Dict[str, Any]:
        """Return configuration."""
        return {
            'metrics': self.metrics,
            'compute_agreement': self.compute_agreement
        }


@register('audit_ops', 'regression')
class RegressionAuditOps(AuditOps):
    """Regression evaluation and metrics computation."""

    def __init__(self, metrics: List[str] = None, **kwargs):
        self.metrics = metrics or ['mse', 'mae', 'r2']
        self.supported_metrics = ['mse', 'mae', 'rmse', 'r2', 'explained_variance']

        # Validate metrics
        for metric in self.metrics:
            if metric not in self.supported_metrics:
                raise ValueError(f"Unsupported metric: {metric}. "
                               f"Supported: {self.supported_metrics}")

    def evaluate(self, model: nn.Module, data_loader: DataLoader,
                 penalty_ops: PenaltyOps, device: str, **kwargs) -> Dict[str, Any]:
        """Evaluate regression model on given data loader."""
        model.eval()

        all_predictions = []
        all_targets = []
        total_loss = 0.0

        print("Evaluating regression model...")

        with torch.no_grad():
            eval_pbar = tqdm(data_loader, desc="Regression Evaluation")
            for batch in eval_pbar:
                data, targets = batch
                data, targets = data.to(device), targets.to(device)

                outputs = model(data)
                loss = penalty_ops.compute_loss(outputs, targets)

                total_loss += loss.item()

                all_predictions.extend(outputs.cpu().numpy().flatten())
                all_targets.extend(targets.cpu().numpy().flatten())

        # Convert to numpy arrays
        predictions = np.array(all_predictions)
        targets = np.array(all_targets)

        # Compute metrics
        results = {
            'loss': total_loss / len(data_loader),
            'num_samples': len(targets)
        }

        # Mean Squared Error
        if 'mse' in self.metrics:
            mse = np.mean((predictions - targets) ** 2)
            results['mse'] = mse

        # Mean Absolute Error
        if 'mae' in self.metrics:
            mae = np.mean(np.abs(predictions - targets))
            results['mae'] = mae

        # Root Mean Squared Error
        if 'rmse' in self.metrics:
            rmse = np.sqrt(np.mean((predictions - targets) ** 2))
            results['rmse'] = rmse

        # R-squared
        if 'r2' in self.metrics:
            ss_res = np.sum((targets - predictions) ** 2)
            ss_tot = np.sum((targets - np.mean(targets)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            results['r2'] = r2

        # Explained Variance Score
        if 'explained_variance' in self.metrics:
            variance_score = 1 - np.var(targets - predictions) / np.var(targets)
            results['explained_variance'] = variance_score

        return results

    def get_config(self) -> Dict[str, Any]:
        """Return configuration."""
        return {'metrics': self.metrics}
