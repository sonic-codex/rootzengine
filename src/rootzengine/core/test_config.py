"""
Test vs Live Configuration Management

Easy switching between test mode (with mocks) and live mode (with real processing).
"""

import os
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class ProcessingMode(Enum):
    """Processing mode configuration."""

    TEST = "test"  # Use mocks, fast processing
    VALIDATION = "validation"  # Real processing, test files
    LIVE = "live"  # Full production processing


@dataclass
class TestConfig:
    """Configuration for test vs live processing."""

    mode: ProcessingMode = ProcessingMode.TEST

    # Test mode settings
    use_mock_stem_separation: bool = True
    use_mock_midi_conversion: bool = True
    use_mock_spectrotone: bool = True
    use_mock_enrichment: bool = True

    # File paths
    test_data_dir: str = "test_dataset"
    live_data_dir: str = "data"

    # Performance settings
    max_processing_time: int = 60  # seconds
    enable_cleanup: bool = False  # Don't delete stems in test mode

    @classmethod
    def from_environment(cls) -> "TestConfig":
        """Create config from environment variables."""
        mode_str = os.getenv("ROOTZENGINE_MODE", "test").lower()

        try:
            mode = ProcessingMode(mode_str)
        except ValueError:
            mode = ProcessingMode.TEST

        config = cls(mode=mode)

        # Override based on mode
        if mode == ProcessingMode.TEST:
            # Fast testing with mocks
            config.use_mock_stem_separation = True
            config.use_mock_midi_conversion = True
            config.use_mock_spectrotone = True
            config.use_mock_enrichment = True
            config.enable_cleanup = False

        elif mode == ProcessingMode.VALIDATION:
            # Real processing but with test files
            config.use_mock_stem_separation = False
            config.use_mock_midi_conversion = False
            config.use_mock_spectrotone = False
            config.use_mock_enrichment = True  # Still mock API calls
            config.enable_cleanup = False

        elif mode == ProcessingMode.LIVE:
            # Full production processing
            config.use_mock_stem_separation = False
            config.use_mock_midi_conversion = False
            config.use_mock_spectrotone = False
            config.use_mock_enrichment = False
            config.enable_cleanup = True

        return config

    def is_test_mode(self) -> bool:
        """Check if running in any test mode."""
        return self.mode in [ProcessingMode.TEST, ProcessingMode.VALIDATION]

    def is_live_mode(self) -> bool:
        """Check if running in live production mode."""
        return self.mode == ProcessingMode.LIVE

    def get_data_dir(self) -> str:
        """Get appropriate data directory for current mode."""
        return self.test_data_dir if self.is_test_mode() else self.live_data_dir


# Global test configuration
_test_config: Optional[TestConfig] = None


def get_test_config() -> TestConfig:
    """Get global test configuration."""
    global _test_config
    if _test_config is None:
        _test_config = TestConfig.from_environment()
    return _test_config


def set_test_mode():
    """Set system to test mode."""
    global _test_config
    _test_config = TestConfig(mode=ProcessingMode.TEST)


def set_validation_mode():
    """Set system to validation mode."""
    global _test_config
    _test_config = TestConfig(mode=ProcessingMode.VALIDATION)


def set_live_mode():
    """Set system to live mode."""
    global _test_config
    _test_config = TestConfig(mode=ProcessingMode.LIVE)
