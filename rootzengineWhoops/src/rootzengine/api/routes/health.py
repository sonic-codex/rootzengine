"""Health check endpoints."""

import logging
import psutil
from typing import Dict, Any
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...core.config import RootzEngineConfig

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    system: Dict[str, Any]
    services: Dict[str, bool]


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model."""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    system: Dict[str, Any]
    services: Dict[str, Any]
    configuration: Dict[str, Any]


def get_config() -> RootzEngineConfig:
    """Dependency to get application configuration."""
    return RootzEngineConfig()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    try:
        # Get system info
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            version="0.1.0",
            uptime_seconds=psutil.boot_time(),
            system={
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            },
            services={
                "audio_analysis": True,
                "midi_generation": True,
                "pattern_detection": True,
                "api": True
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(timezone.utc),
            version="0.1.0",
            uptime_seconds=0,
            system={},
            services={
                "audio_analysis": False,
                "midi_generation": False,
                "pattern_detection": False,
                "api": False
            }
        )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(config: RootzEngineConfig = Depends(get_config)):
    """Detailed health check with configuration and service status."""
    try:
        # System information
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check service dependencies
        services = {
            "audio_analysis": _check_audio_analysis(),
            "midi_generation": _check_midi_generation(),
            "pattern_detection": _check_pattern_detection(),
            "storage": _check_storage(config),
            "azure_services": _check_azure_services(config)
        }
        
        # Configuration info (safe subset)
        config_info = {
            "audio": {
                "sample_rate": config.audio.sample_rate,
                "hop_length": config.audio.hop_length,
                "n_fft": config.audio.n_fft
            },
            "processing": {
                "workers": config.workers,
                "debug": config.debug,
                "log_level": config.log_level
            },
            "directories": {
                "data_dir": str(config.data_dir),
                "output_dir": str(config.output_dir),
                "cache_dir": str(config.cache_dir)
            }
        }
        
        # Overall health status
        overall_status = "healthy" if all(services.values()) else "degraded"
        
        return DetailedHealthResponse(
            status=overall_status,
            timestamp=datetime.now(timezone.utc),
            version="0.1.0",
            uptime_seconds=psutil.boot_time(),
            system={
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "memory_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_percent": disk.percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                "platform": psutil.os.name
            },
            services=services,
            configuration=config_info
        )
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return DetailedHealthResponse(
            status="unhealthy",
            timestamp=datetime.now(timezone.utc),
            version="0.1.0",
            uptime_seconds=0,
            system={},
            services={},
            configuration={}
        )


@router.get("/ready")
async def readiness_check():
    """Kubernetes-style readiness check."""
    try:
        # Basic service readiness checks
        checks = {
            "audio_analysis": _check_audio_analysis(),
            "midi_generation": _check_midi_generation(),
            "pattern_detection": _check_pattern_detection()
        }
        
        if all(checks.values()):
            return {"status": "ready", "checks": checks}
        else:
            return {"status": "not_ready", "checks": checks}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e)}


@router.get("/live")
async def liveness_check():
    """Kubernetes-style liveness check."""
    try:
        # Simple liveness check - if we can respond, we're alive
        return {"status": "alive", "timestamp": datetime.now(timezone.utc)}
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return {"status": "dead", "error": str(e)}


def _check_audio_analysis() -> bool:
    """Check if audio analysis components are working."""
    try:
        from ...audio.analysis import AudioStructureAnalyzer
        from ...audio.features import FeatureExtractor
        
        # Try to initialize components
        analyzer = AudioStructureAnalyzer()
        extractor = FeatureExtractor()
        
        return True
    except Exception as e:
        logger.warning(f"Audio analysis check failed: {e}")
        return False


def _check_midi_generation() -> bool:
    """Check if MIDI generation components are working."""
    try:
        from ...midi.converter import AudioToMIDIConverter
        from ...midi.patterns import ReggaePatternLibrary
        
        # Try to initialize components
        converter = AudioToMIDIConverter()
        library = ReggaePatternLibrary()
        
        return True
    except Exception as e:
        logger.warning(f"MIDI generation check failed: {e}")
        return False


def _check_pattern_detection() -> bool:
    """Check if reggae pattern detection is working."""
    try:
        from ...audio.reggae_patterns import ReggaePatternDetector
        
        # Try to initialize component
        detector = ReggaePatternDetector()
        
        return True
    except Exception as e:
        logger.warning(f"Pattern detection check failed: {e}")
        return False


def _check_storage(config: RootzEngineConfig) -> bool:
    """Check if storage directories are accessible."""
    try:
        # Check if directories exist and are writable
        directories = [config.data_dir, config.output_dir, config.cache_dir]
        
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            
            # Try to write a test file
            test_file = directory / "health_check_test.tmp"
            test_file.write_text("health check")
            test_file.unlink()
        
        return True
    except Exception as e:
        logger.warning(f"Storage check failed: {e}")
        return False


def _check_azure_services(config: RootzEngineConfig) -> bool:
    """Check if Azure services are configured and accessible."""
    try:
        if not config.azure:
            return True  # Not configured, but that's okay
        
        # TODO: Add actual Azure connectivity checks when Azure module is implemented
        return True
        
    except Exception as e:
        logger.warning(f"Azure services check failed: {e}")
        return False