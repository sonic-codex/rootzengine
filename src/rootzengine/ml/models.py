"""
ML model definitions for reggae music analysis.

Provides models for:
- Reggae pattern classification (one-drop, steppers, rockers)
- Tempo detection
- Instrument classification
- Style classification
"""

from typing import Any, List, Optional, Dict, Tuple
import logging
from pathlib import Path
import pickle

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class ReggaePatternCNN(nn.Module if TORCH_AVAILABLE else object):
    """
    Convolutional Neural Network for reggae pattern classification.

    Classifies audio features into reggae patterns (one-drop, steppers, rockers, etc.)
    """

    def __init__(self, input_size: int = 128, num_classes: int = 5):
        """
        Initialize the CNN.

        Args:
            input_size: Size of input feature vector
            num_classes: Number of pattern classes
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for CNN models")

        super().__init__()

        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(32)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(64)
        self.conv3 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(128)

        self.pool = nn.MaxPool1d(2)
        self.dropout = nn.Dropout(0.3)

        # Calculate flattened size
        self.flat_size = 128 * (input_size // 8)

        self.fc1 = nn.Linear(self.flat_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x):
        """Forward pass."""
        # Input shape: (batch, features)
        x = x.unsqueeze(1)  # Add channel dimension: (batch, 1, features)

        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))

        x = x.view(x.size(0), -1)  # Flatten
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.dropout(F.relu(self.fc2(x)))
        x = self.fc3(x)

        return x


class ReggaeClassifier:
    """
    Classifier for detecting reggae music patterns.

    Supports both traditional ML (Random Forest) and deep learning (CNN) backends.
    """

    def __init__(
        self,
        model_type: str = "random_forest",
        num_classes: int = 5,
        input_size: int = 128,
    ):
        """
        Initialize the classifier.

        Args:
            model_type: Type of model ('random_forest', 'gradient_boosting', 'cnn')
            num_classes: Number of pattern classes
            input_size: Size of input feature vector
        """
        self.model_type = model_type
        self.num_classes = num_classes
        self.input_size = input_size
        self.is_trained = False
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None

        # Initialize model based on type
        if model_type == "random_forest":
            if not SKLEARN_AVAILABLE:
                raise ImportError("scikit-learn is required for Random Forest")
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                random_state=42,
            )
        elif model_type == "gradient_boosting":
            if not SKLEARN_AVAILABLE:
                raise ImportError("scikit-learn is required for Gradient Boosting")
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
            )
        elif model_type == "cnn":
            if not TORCH_AVAILABLE:
                raise ImportError("PyTorch is required for CNN")
            self.model = ReggaePatternCNN(input_size=input_size, num_classes=num_classes)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        validation_split: float = 0.2,
        epochs: int = 50,
        batch_size: int = 32,
    ) -> Dict[str, Any]:
        """
        Train the classifier.

        Args:
            X: Training features (n_samples, n_features)
            y: Training labels (n_samples,)
            validation_split: Fraction of data to use for validation
            epochs: Number of training epochs (for CNN)
            batch_size: Batch size (for CNN)

        Returns:
            Training history/metrics
        """
        if len(X) == 0:
            logger.warning("No training data provided")
            return {"status": "no_data"}

        # Scale features
        if self.scaler is not None:
            X = self.scaler.fit_transform(X)

        if self.model_type in ["random_forest", "gradient_boosting"]:
            # Traditional ML training
            self.model.fit(X, y)
            self.is_trained = True

            # Get training accuracy
            train_acc = self.model.score(X, y)

            return {
                "status": "completed",
                "train_accuracy": float(train_acc),
                "model_type": self.model_type,
            }

        elif self.model_type == "cnn":
            # Deep learning training
            return self._train_cnn(X, y, validation_split, epochs, batch_size)

    def _train_cnn(
        self,
        X: np.ndarray,
        y: np.ndarray,
        validation_split: float,
        epochs: int,
        batch_size: int,
    ) -> Dict[str, Any]:
        """Train CNN model."""
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )

        # Convert to tensors
        X_train = torch.FloatTensor(X_train).to(self.device)
        y_train = torch.LongTensor(y_train).to(self.device)
        X_val = torch.FloatTensor(X_val).to(self.device)
        y_val = torch.LongTensor(y_val).to(self.device)

        # Setup training
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)

        history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

        # Training loop
        for epoch in range(epochs):
            self.model.train()
            train_loss = 0.0
            correct = 0
            total = 0

            # Mini-batch training
            for i in range(0, len(X_train), batch_size):
                batch_X = X_train[i:i+batch_size]
                batch_y = y_train[i:i+batch_size]

                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                train_loss += loss.item()
                _, predicted = outputs.max(1)
                total += batch_y.size(0)
                correct += predicted.eq(batch_y).sum().item()

            train_acc = correct / total

            # Validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val)
                val_loss = criterion(val_outputs, y_val).item()
                _, val_predicted = val_outputs.max(1)
                val_acc = val_predicted.eq(y_val).sum().item() / len(y_val)

            history["train_loss"].append(train_loss / (len(X_train) / batch_size))
            history["val_loss"].append(val_loss)
            history["train_acc"].append(train_acc)
            history["val_acc"].append(val_acc)

            if (epoch + 1) % 10 == 0:
                logger.info(
                    f"Epoch {epoch+1}/{epochs} - "
                    f"Train Loss: {history['train_loss'][-1]:.4f}, "
                    f"Val Loss: {val_loss:.4f}, "
                    f"Train Acc: {train_acc:.4f}, "
                    f"Val Acc: {val_acc:.4f}"
                )

        self.is_trained = True

        return {
            "status": "completed",
            "history": history,
            "final_train_acc": history["train_acc"][-1],
            "final_val_acc": history["val_acc"][-1],
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Input features (n_samples, n_features)

        Returns:
            Predicted class labels (n_samples,)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Scale features
        if self.scaler is not None:
            X = self.scaler.transform(X)

        if self.model_type in ["random_forest", "gradient_boosting"]:
            return self.model.predict(X)
        elif self.model_type == "cnn":
            self.model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X).to(self.device)
                outputs = self.model(X_tensor)
                _, predicted = outputs.max(1)
                return predicted.cpu().numpy()

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.

        Args:
            X: Input features (n_samples, n_features)

        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Scale features
        if self.scaler is not None:
            X = self.scaler.transform(X)

        if self.model_type in ["random_forest", "gradient_boosting"]:
            return self.model.predict_proba(X)
        elif self.model_type == "cnn":
            self.model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X).to(self.device)
                outputs = self.model(X_tensor)
                probas = F.softmax(outputs, dim=1)
                return probas.cpu().numpy()

    def save(self, path: str):
        """Save model to disk."""
        save_dict = {
            "model_type": self.model_type,
            "num_classes": self.num_classes,
            "input_size": self.input_size,
            "is_trained": self.is_trained,
            "scaler": self.scaler,
        }

        if self.model_type in ["random_forest", "gradient_boosting"]:
            save_dict["model"] = self.model
        elif self.model_type == "cnn":
            save_dict["model_state_dict"] = self.model.state_dict()

        with open(path, "wb") as f:
            pickle.dump(save_dict, f)

        logger.info(f"Model saved to {path}")

    def load(self, path: str):
        """Load model from disk."""
        with open(path, "rb") as f:
            save_dict = pickle.load(f)

        self.model_type = save_dict["model_type"]
        self.num_classes = save_dict["num_classes"]
        self.input_size = save_dict["input_size"]
        self.is_trained = save_dict["is_trained"]
        self.scaler = save_dict["scaler"]

        if self.model_type in ["random_forest", "gradient_boosting"]:
            self.model = save_dict["model"]
        elif self.model_type == "cnn":
            self.model = ReggaePatternCNN(
                input_size=self.input_size,
                num_classes=self.num_classes,
            )
            self.model.load_state_dict(save_dict["model_state_dict"])
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)

        logger.info(f"Model loaded from {path}")


__all__ = [
    "ReggaeClassifier",
    "ReggaePatternCNN",
]
