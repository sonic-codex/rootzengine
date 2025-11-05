"""
Model training functionality for reggae pattern classification.

Provides high-level training functions and utilities for training
reggae pattern classifiers on audio feature datasets.
"""

from typing import Optional, Any, Dict, Tuple
from pathlib import Path
import logging

import numpy as np

from .models import ReggaeClassifier
from ..core.config import MLConfig

logger = logging.getLogger(__name__)


def train_model(
    data: Optional[Any] = None,
    config: Optional[MLConfig] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Train a machine learning model for audio pattern detection.

    Args:
        data: Training data (can be None for testing). Should be tuple of (X, y)
        config: ML configuration object
        **kwargs: Additional training parameters

    Returns:
        Dictionary containing training results and metrics
    """
    if data is None:
        logger.info("No training data provided, skipping training")
        return {
            'status': 'skipped',
            'reason': 'no_data',
            'model_path': None
        }

    logger.info("Starting model training")

    # Unpack data
    if isinstance(data, tuple) and len(data) == 2:
        X_train, y_train = data
    else:
        logger.error("Data must be a tuple of (X, y)")
        return {
            'status': 'error',
            'reason': 'invalid_data_format',
            'model_path': None
        }

    # Get configuration
    if config is None:
        from ..core.config import RootzEngineConfig
        config = RootzEngineConfig().ml

    # Override config with kwargs
    model_type = kwargs.get('model_type', 'random_forest')
    num_classes = kwargs.get('num_classes', 5)
    input_size = kwargs.get('input_size', X_train.shape[1] if len(X_train.shape) > 1 else 128)

    # Initialize model
    model = ReggaeClassifier(
        model_type=model_type,
        num_classes=num_classes,
        input_size=input_size,
    )

    # Train model
    try:
        history = model.fit(
            X_train,
            y_train,
            validation_split=kwargs.get('validation_split', 0.2),
            epochs=kwargs.get('epochs', config.num_epochs),
            batch_size=kwargs.get('batch_size', config.batch_size),
        )
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return {
            'status': 'error',
            'reason': str(e),
            'model_path': None
        }

    # Save model
    model_path = kwargs.get('model_path', config.checkpoint_dir + '/trained_model.pkl')
    model_dir = Path(model_path).parent
    model_dir.mkdir(parents=True, exist_ok=True)

    try:
        model.save(model_path)
    except Exception as e:
        logger.warning(f"Failed to save model: {e}")
        model_path = None

    # Prepare result
    result = {
        'status': 'completed',
        'model_path': str(model_path) if model_path else None,
        'model_type': model_type,
        'num_classes': num_classes,
        'training_samples': len(X_train),
    }

    # Add metrics from history
    if 'train_accuracy' in history:
        result['accuracy'] = history['train_accuracy']
    elif 'final_val_acc' in history:
        result['accuracy'] = history['final_val_acc']
        result['train_accuracy'] = history['final_train_acc']
        result['val_accuracy'] = history['final_val_acc']

    logger.info(f"Training completed with accuracy: {result.get('accuracy', 'N/A')}")

    return result


def prepare_training_data(
    audio_files: list,
    labels: list,
    feature_extractor=None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare training data from audio files.

    Args:
        audio_files: List of paths to audio files
        labels: List of labels corresponding to audio files
        feature_extractor: Feature extraction function (optional)

    Returns:
        Tuple of (X, y) where X is features and y is labels
    """
    if feature_extractor is None:
        # Use default feature extraction
        from ..audio.features import extract_features

        def default_extractor(audio_path):
            features = extract_features(audio_path)
            # Flatten all features into a single vector
            feature_vector = []
            for key in sorted(features.keys()):
                value = features[key]
                if isinstance(value, (list, np.ndarray)):
                    feature_vector.extend(np.array(value).flatten())
                elif isinstance(value, (int, float)):
                    feature_vector.append(value)
            return np.array(feature_vector)

        feature_extractor = default_extractor

    X = []
    y = []

    for audio_file, label in zip(audio_files, labels):
        try:
            features = feature_extractor(audio_file)
            X.append(features)
            y.append(label)
        except Exception as e:
            logger.warning(f"Failed to extract features from {audio_file}: {e}")
            continue

    return np.array(X), np.array(y)


def evaluate_model(
    model: ReggaeClassifier,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> Dict[str, Any]:
    """
    Evaluate a trained model.

    Args:
        model: Trained classifier
        X_test: Test features
        y_test: Test labels

    Returns:
        Dictionary of evaluation metrics
    """
    try:
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return {'error': str(e)}

    # Calculate metrics
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
        'num_samples': len(y_test),
    }

    logger.info(f"Evaluation metrics: {metrics}")

    return metrics


__all__ = [
    "train_model",
    "prepare_training_data",
    "evaluate_model",
]
