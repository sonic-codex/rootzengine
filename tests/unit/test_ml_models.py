"""Tests for ML models"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from rootzengine.ml.models import ReggaeClassifier
from rootzengine.ml.training import train_model, prepare_training_data, evaluate_model


class TestReggaeClassifier:
    """Test ReggaeClassifier"""

    @pytest.fixture
    def sample_data(self):
        """Generate sample training data"""
        np.random.seed(42)
        X = np.random.randn(100, 128)  # 100 samples, 128 features
        y = np.random.randint(0, 5, 100)  # 5 classes
        return X, y

    def test_random_forest_initialization(self):
        """Test Random Forest model initialization"""
        model = ReggaeClassifier(model_type="random_forest", num_classes=5)

        assert model.model_type == "random_forest"
        assert model.num_classes == 5
        assert model.is_trained is False

    def test_random_forest_training(self, sample_data):
        """Test training Random Forest model"""
        X, y = sample_data
        model = ReggaeClassifier(model_type="random_forest", num_classes=5)

        history = model.fit(X, y)

        assert model.is_trained is True
        assert "status" in history
        assert history["status"] == "completed"
        assert "train_accuracy" in history

    def test_random_forest_prediction(self, sample_data):
        """Test Random Forest predictions"""
        X, y = sample_data
        model = ReggaeClassifier(model_type="random_forest", num_classes=5)

        model.fit(X, y)
        predictions = model.predict(X[:10])

        assert len(predictions) == 10
        assert all(0 <= p < 5 for p in predictions)

    def test_random_forest_predict_proba(self, sample_data):
        """Test Random Forest probability predictions"""
        X, y = sample_data
        model = ReggaeClassifier(model_type="random_forest", num_classes=5)

        model.fit(X, y)
        probabilities = model.predict_proba(X[:10])

        assert probabilities.shape == (10, 5)
        # Each row should sum to 1
        np.testing.assert_array_almost_equal(probabilities.sum(axis=1), np.ones(10), decimal=5)

    def test_predict_before_training_raises_error(self, sample_data):
        """Test that predicting before training raises error"""
        X, y = sample_data
        model = ReggaeClassifier(model_type="random_forest", num_classes=5)

        with pytest.raises(ValueError, match="Model must be trained"):
            model.predict(X[:10])

    def test_gradient_boosting_model(self, sample_data):
        """Test Gradient Boosting model"""
        X, y = sample_data
        model = ReggaeClassifier(model_type="gradient_boosting", num_classes=5)

        history = model.fit(X, y)

        assert model.is_trained is True
        assert history["status"] == "completed"

    def test_save_and_load_model(self, sample_data):
        """Test saving and loading model"""
        X, y = sample_data
        model = ReggaeClassifier(model_type="random_forest", num_classes=5)

        model.fit(X, y)

        # Save model
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "test_model.pkl"
            model.save(str(model_path))

            # Load model
            loaded_model = ReggaeClassifier(model_type="random_forest", num_classes=5)
            loaded_model.load(str(model_path))

            assert loaded_model.is_trained is True
            assert loaded_model.model_type == "random_forest"

            # Test predictions match
            original_pred = model.predict(X[:10])
            loaded_pred = loaded_model.predict(X[:10])

            np.testing.assert_array_equal(original_pred, loaded_pred)


class TestTrainModel:
    """Test train_model function"""

    @pytest.fixture
    def sample_data(self):
        """Generate sample training data"""
        np.random.seed(42)
        X = np.random.randn(100, 128)
        y = np.random.randint(0, 5, 100)
        return X, y

    def test_train_model_with_data(self, sample_data):
        """Test training with data"""
        result = train_model(
            data=sample_data,
            model_type="random_forest",
            num_classes=5,
        )

        assert result["status"] == "completed"
        assert "accuracy" in result
        assert result["model_type"] == "random_forest"

    def test_train_model_without_data(self):
        """Test training without data (should skip)"""
        result = train_model(data=None)

        assert result["status"] == "skipped"
        assert result["reason"] == "no_data"

    def test_train_model_invalid_data_format(self):
        """Test training with invalid data format"""
        result = train_model(data="invalid")

        assert result["status"] == "error"

    def test_train_model_with_config(self, sample_data):
        """Test training with custom configuration"""
        from rootzengine.core.config import MLConfig

        config = MLConfig(batch_size=16, num_epochs=10)

        result = train_model(
            data=sample_data,
            config=config,
            model_type="random_forest",
        )

        assert result["status"] == "completed"


class TestPrepareTrainingData:
    """Test prepare_training_data function"""

    def test_prepare_empty_data(self):
        """Test with empty audio files list"""
        X, y = prepare_training_data([], [])

        assert len(X) == 0
        assert len(y) == 0

    def test_feature_extractor_called(self, mocker):
        """Test that feature extractor is called"""
        # Mock feature extractor
        mock_extractor = mocker.MagicMock(return_value=np.random.randn(128))

        audio_files = ["audio1.wav", "audio2.wav"]
        labels = [0, 1]

        X, y = prepare_training_data(audio_files, labels, feature_extractor=mock_extractor)

        assert mock_extractor.call_count == 2
        assert len(X) == 2
        assert len(y) == 2


class TestEvaluateModel:
    """Test evaluate_model function"""

    @pytest.fixture
    def trained_model(self):
        """Create a trained model"""
        np.random.seed(42)
        X = np.random.randn(100, 128)
        y = np.random.randint(0, 5, 100)

        model = ReggaeClassifier(model_type="random_forest", num_classes=5)
        model.fit(X, y)

        return model

    def test_evaluate_model(self, trained_model):
        """Test model evaluation"""
        np.random.seed(42)
        X_test = np.random.randn(20, 128)
        y_test = np.random.randint(0, 5, 20)

        metrics = evaluate_model(trained_model, X_test, y_test)

        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert metrics["num_samples"] == 20

    def test_evaluate_model_metrics_range(self, trained_model):
        """Test that evaluation metrics are in valid range"""
        np.random.seed(42)
        X_test = np.random.randn(20, 128)
        y_test = np.random.randint(0, 5, 20)

        metrics = evaluate_model(trained_model, X_test, y_test)

        # All metrics should be between 0 and 1
        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["precision"] <= 1
        assert 0 <= metrics["recall"] <= 1
        assert 0 <= metrics["f1_score"] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
