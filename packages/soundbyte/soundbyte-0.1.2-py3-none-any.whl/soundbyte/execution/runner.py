"""
Experiment runner for SoundByte.

This module orchestrates the complete ML experiment pipeline,
managing component creation, training, and evaluation.
"""

import torch
import random
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path

from ..config.experiment import ExperimentConfig
from ..core.factory import ComponentFactory, auto_device
from ..plugins.registry import get_registry_stats


class ExperimentRunner:
    """Main experiment orchestrator for SoundByte."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.components = {}
        self.models = {}

    def _set_random_seeds(self):
        """Set random seeds for reproducibility."""
        torch.manual_seed(self.config.seed)
        torch.cuda.manual_seed_all(self.config.seed)
        np.random.seed(self.config.seed)
        random.seed(self.config.seed)

        # Ensure deterministic behavior
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    def _setup_device(self) -> str:
        """Setup and return the device to use."""
        if self.config.device == "auto":
            device = auto_device()
        else:
            device = self.config.device

        # Validate device availability
        if device == "cuda" and not torch.cuda.is_available():
            print("Warning: CUDA not available, falling back to CPU")
            device = "cpu"
        elif device == "mps" and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
            print("Warning: MPS not available, falling back to CPU")
            device = "cpu"

        return device

    def _create_components(self, device: str):
        """Create all required components."""
        print("Creating Components...")

        # Data operations
        print("  Creating Data Operations...")
        self.components['data_ops'] = ComponentFactory.create_data_ops(self.config.data_ops)

        # Model operations
        if self.config.model_ops:
            print("  Creating Model Operations...")
            self.components['model_ops'] = ComponentFactory.create_model_ops(self.config.model_ops, device)
            self.models['main'] = self.components['model_ops'].get_model()

        # Teacher and student models for distillation
        if self.config.teacher_model_ops:
            print("  Creating Teacher Model Operations...")
            self.components['teacher_model_ops'] = ComponentFactory.create_model_ops(self.config.teacher_model_ops, device)
            self.models['teacher'] = self.components['teacher_model_ops'].get_model()

        if self.config.student_model_ops:
            print("  Creating Student Model Operations...")
            self.components['student_model_ops'] = ComponentFactory.create_model_ops(self.config.student_model_ops, device)
            self.models['student'] = self.components['student_model_ops'].get_model()

        # Penalty operations
        if self.config.penalty_ops:
            print("  Creating Penalty Operations...")
            self.components['penalty_ops'] = ComponentFactory.create_penalty_ops(self.config.penalty_ops)

        if self.config.distillation_penalty_ops:
            print("  Creating Distillation Penalty Operations...")
            self.components['distillation_penalty_ops'] = ComponentFactory.create_penalty_ops(self.config.distillation_penalty_ops)

        # Control operations
        print("  Creating Control Operations...")
        self.components['control_ops'] = ComponentFactory.create_control_ops(self.config.control_ops)

        # Schedule operations
        if self.config.schedule_ops:
            print("  Creating Schedule Operations...")
            self.components['schedule_ops'] = ComponentFactory.create_schedule_ops(self.config.schedule_ops)

        # Train operations
        print("  Creating Train Operations...")
        self.components['train_ops'] = ComponentFactory.create_train_ops(self.config.train_ops)

        # Audit operations
        print("  Creating Audit Operations...")
        self.components['audit_ops'] = ComponentFactory.create_audit_ops(self.config.audit_ops)

        print("Components created successfully!")
        print()

    def _run_classification(self, device: str) -> Dict[str, Any]:
        """Run classification training."""
        if 'main' not in self.models:
            raise ValueError("No main model found for classification")

        model = self.models['main']
        penalty_ops = self.components.get('penalty_ops')

        if penalty_ops is None:
            raise ValueError("No penalty operations found for classification")

        return self.components['train_ops'].train(
            model=model,
            data_ops=self.components['data_ops'],
            control_ops=self.components['control_ops'],
            penalty_ops=penalty_ops,
            audit_ops=self.components['audit_ops'],
            device=device,
            schedule_ops=self.components.get('schedule_ops'),
            output_dir=self.config.output_dir
        )

    def _run_distillation(self, device: str) -> Dict[str, Any]:
        """Run knowledge distillation training."""
        if 'teacher' not in self.models or 'student' not in self.models:
            raise ValueError("Both teacher and student models required for distillation")

        teacher_model = self.models['teacher']
        student_model = self.models['student']
        penalty_ops = self.components.get('distillation_penalty_ops')

        if penalty_ops is None:
            raise ValueError("No distillation penalty operations found")

        return self.components['train_ops'].train(
            model=student_model,
            data_ops=self.components['data_ops'],
            control_ops=self.components['control_ops'],
            penalty_ops=penalty_ops,
            audit_ops=self.components['audit_ops'],
            device=device,
            schedule_ops=self.components.get('schedule_ops'),
            output_dir=self.config.output_dir,
            teacher_model=teacher_model
        )

    def run(self) -> Dict[str, Any]:
        """Run the complete experiment."""
        print(f"Initializing SoundByte Experiment: {self.config.name}")

        # Create output directory
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"Output Directory: {self.config.output_dir}")

        # Set random seeds
        self._set_random_seeds()

        # Setup device
        device = self._setup_device()
        print(f"Device: {device}")
        print(f"Seed: {self.config.seed}")
        print()

        # Create components
        self._create_components(device)

        # Determine experiment type and run
        try:
            if self.config.teacher_model_ops and self.config.student_model_ops:
                # Knowledge distillation
                print("Running Knowledge Distillation Training...")
                results = self._run_distillation(device)
            else:
                # Standard classification
                print("Running Classification Training...")
                results = self._run_classification(device)

            # Save final model if requested
            if self.config.save_model:
                if 'student' in self.models:
                    # Save student model for distillation
                    model_path = output_path / 'final_student_model.pth'
                    torch.save(self.models['student'].state_dict(), model_path)
                    print(f"Final student model saved: {model_path}")
                elif 'main' in self.models:
                    # Save main model for classification
                    model_path = output_path / 'final_model.pth'
                    torch.save(self.models['main'].state_dict(), model_path)
                    print(f"Final model saved: {model_path}")

            return results

        except Exception as e:
            print(f"Experiment failed: {e}")
            raise

    def get_component_summary(self) -> Dict[str, Any]:
        """Get summary of created components."""
        summary = {
            'experiment_name': self.config.name,
            'device': self.config.device,
            'seed': self.config.seed,
            'components': {},
            'models': list(self.models.keys()),
            'registry_stats': get_registry_stats()
        }

        for name, component in self.components.items():
            summary['components'][name] = {
                'type': type(component).__name__,
                'config': component.get_config()
            }

        return summary


def run_experiment(config_path: str) -> Dict[str, Any]:
    """Convenience function to run an experiment from a config file."""
    from ..config.experiment import load_config

    config = load_config(config_path)
    runner = ExperimentRunner(config)
    return runner.run()
