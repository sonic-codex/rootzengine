"""Audio analysis API endpoints."""

import logging
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, status, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ...audio.analysis import AudioStructureAnalyzer
from ...midi.converter import AudioToMIDIConverter
from ...core.config import RootzEngineConfig
from ...core.exceptions import RootzEngineError, AudioProcessingError, MidiConversionError

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory job storage (use Redis in production)
analysis_jobs = {}
midi_jobs = {}


class AnalysisRequest(BaseModel):
    """Request model for audio analysis."""
    include_midi: bool = Field(False, description="Whether to generate MIDI output")
    riddim_type: Optional[str] = Field(None, description="Force specific riddim type")
    instruments: Optional[List[str]] = Field(None, description="Instruments to include in MIDI")


class AnalysisResponse(BaseModel):
    """Response model for audio analysis."""
    job_id: str
    status: str
    message: str
    analysis: Optional[Dict[str, Any]] = None
    midi_file_url: Optional[str] = None
    processing_time: Optional[float] = None


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis."""
    job_name: Optional[str] = Field(None, description="Optional job name")
    include_midi: bool = Field(False, description="Whether to generate MIDI for all files")
    riddim_type: Optional[str] = Field(None, description="Force specific riddim type")
    instruments: Optional[List[str]] = Field(None, description="Instruments to include in MIDI")


class JobStatus(BaseModel):
    """Job status response model."""
    job_id: str
    status: str  # pending, processing, completed, failed
    message: str
    progress: float = 0.0
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio file to analyze"),
    include_midi: bool = Query(False, description="Generate MIDI output"),
    riddim_type: Optional[str] = Query(None, description="Force specific riddim type"),
    instruments: Optional[str] = Query(None, description="Comma-separated list of instruments")
):
    """
    Analyze an audio file for reggae patterns and structure.
    
    Supported audio formats: WAV, MP3, FLAC, AAC
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file extension
    allowed_extensions = {'.wav', '.mp3', '.flac', '.aac', '.m4a'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Parse instruments
    instrument_list = None
    if instruments:
        instrument_list = [inst.strip() for inst in instruments.split(',')]
    
    # Create job
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "status": "pending",
        "message": "Analysis queued",
        "progress": 0.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "result": None,
        "error": None
    }
    analysis_jobs[job_id] = job_data
    
    # Queue background analysis
    background_tasks.add_task(
        _process_analysis,
        job_id,
        file,
        include_midi,
        riddim_type,
        instrument_list
    )
    
    return AnalysisResponse(
        job_id=job_id,
        status="pending",
        message="Analysis started. Use /status/{job_id} to check progress."
    )


@router.post("/batch", response_model=Dict[str, Any])
async def batch_analyze(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="Audio files to analyze"),
    job_name: Optional[str] = Query(None, description="Optional job name"),
    include_midi: bool = Query(False, description="Generate MIDI for all files"),
    riddim_type: Optional[str] = Query(None, description="Force specific riddim type"),
    instruments: Optional[str] = Query(None, description="Comma-separated list of instruments")
):
    """
    Batch analyze multiple audio files.
    
    Returns a batch job ID that can be used to track progress.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    if len(files) > 50:  # Limit batch size
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch size limited to 50 files"
        )
    
    # Parse instruments
    instrument_list = None
    if instruments:
        instrument_list = [inst.strip() for inst in instruments.split(',')]
    
    # Create batch job
    batch_job_id = str(uuid.uuid4())
    batch_job_data = {
        "job_id": batch_job_id,
        "status": "pending",
        "message": "Batch analysis queued",
        "progress": 0.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "total_files": len(files),
        "completed_files": 0,
        "failed_files": 0,
        "file_jobs": [],
        "result": None,
        "error": None
    }
    analysis_jobs[batch_job_id] = batch_job_data
    
    # Queue background batch processing
    background_tasks.add_task(
        _process_batch_analysis,
        batch_job_id,
        files,
        job_name or f"Batch_{batch_job_id[:8]}",
        include_midi,
        riddim_type,
        instrument_list
    )
    
    return {
        "batch_job_id": batch_job_id,
        "status": "pending",
        "message": f"Batch analysis started for {len(files)} files",
        "total_files": len(files)
    }


@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of an analysis job."""
    if job_id not in analysis_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_data = analysis_jobs[job_id]
    return JobStatus(**job_data)


@router.get("/results/{job_id}")
async def get_analysis_results(job_id: str):
    """Get the results of a completed analysis job."""
    if job_id not in analysis_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_data = analysis_jobs[job_id]
    
    if job_data["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job not completed. Current status: {job_data['status']}"
        )
    
    return job_data["result"]


@router.get("/download/midi/{job_id}")
async def download_midi(job_id: str):
    """Download generated MIDI file."""
    if job_id not in analysis_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_data = analysis_jobs[job_id]
    
    if job_data["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job not completed"
        )
    
    result = job_data.get("result", {})
    midi_path = result.get("midi_file_path")
    
    if not midi_path or not Path(midi_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MIDI file not found"
        )
    
    return FileResponse(
        midi_path,
        media_type="audio/midi",
        filename=f"reggae_analysis_{job_id[:8]}.mid"
    )


@router.get("/supported-riddims")
async def get_supported_riddims():
    """Get list of supported reggae riddim types."""
    try:
        converter = AudioToMIDIConverter()
        riddims = converter.get_supported_riddims()
        
        # Get detailed info for each riddim
        riddim_info = {}
        from ...midi.patterns import RiddimType, ReggaePatternLibrary
        
        library = ReggaePatternLibrary()
        for riddim_name in riddims:
            try:
                riddim_type = RiddimType(riddim_name)
                info = library.get_riddim_info(riddim_type)
                info["available_instruments"] = library.get_available_instruments(riddim_type)
                info["tempo_range"] = library.get_compatible_tempo(riddim_type)
                riddim_info[riddim_name] = info
            except ValueError:
                continue
        
        return {
            "supported_riddims": riddims,
            "riddim_details": riddim_info
        }
        
    except Exception as e:
        logger.error(f"Error getting supported riddims: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving supported riddim types"
        )


@router.get("/supported-instruments")
async def get_supported_instruments(riddim_type: Optional[str] = Query(None)):
    """Get list of supported instruments for MIDI generation."""
    try:
        converter = AudioToMIDIConverter()
        
        if riddim_type:
            instruments = converter.get_available_instruments(riddim_type)
            return {
                "riddim_type": riddim_type,
                "instruments": instruments
            }
        else:
            # Get all instruments across all riddim types
            all_instruments = set()
            for riddim in converter.get_supported_riddims():
                instruments = converter.get_available_instruments(riddim)
                all_instruments.update(instruments)
            
            return {
                "all_instruments": list(all_instruments),
                "note": "Use riddim_type parameter to get instruments for specific riddim"
            }
            
    except Exception as e:
        logger.error(f"Error getting supported instruments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving supported instruments"
        )


@router.get("/structure/{file_id}")
async def analyze_structure(file_id: str) -> Dict[str, Any]:
    """Analyze audio structure"""
    # TODO: Implement structure analysis
    return {
        "file_id": file_id,
        "structure": {
            "sections": [],
            "tempo": 120.0,
            "key": "C major"
        }
    }


@router.get("/features/{file_id}")
async def extract_features(file_id: str) -> Dict[str, Any]:
    """Extract audio features"""
    # TODO: Implement feature extraction
    return {
        "file_id": file_id,
        "features": {
            "mfcc": [],
            "spectral_centroid": [],
            "chroma": []
        }
    }


async def _process_analysis(
    job_id: str,
    file: UploadFile,
    include_midi: bool,
    riddim_type: Optional[str],
    instruments: Optional[List[str]]
):
    """Process analysis in background."""
    job_data = analysis_jobs[job_id]
    
    try:
        # Update job status
        job_data["status"] = "processing"
        job_data["message"] = "Analyzing audio file..."
        job_data["progress"] = 0.1
        job_data["updated_at"] = datetime.now()
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Initialize analyzer
            config = RootzEngineConfig()
            analyzer = AudioStructureAnalyzer(config.audio)
            
            # Update progress
            job_data["progress"] = 0.3
            job_data["message"] = "Performing structure analysis..."
            
            # Analyze audio
            analysis = analyzer.analyze_structure(tmp_file_path)
            
            # Update progress
            job_data["progress"] = 0.6
            
            result = {
                "analysis": analysis,
                "file_name": file.filename,
                "processing_time": None
            }
            
            # Generate MIDI if requested
            if include_midi:
                job_data["message"] = "Generating MIDI..."
                job_data["progress"] = 0.8
                
                converter = AudioToMIDIConverter(config.audio)
                
                # Create output directory
                output_dir = config.output_dir / "midi" / job_id
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate MIDI
                from ...midi.patterns import RiddimType
                force_riddim = None
                if riddim_type:
                    try:
                        force_riddim = RiddimType(riddim_type)
                    except ValueError:
                        pass
                
                midi_path = converter.convert_to_midi(
                    tmp_file_path,
                    str(output_dir / f"{job_id}.mid"),
                    analysis,
                    instruments,
                    force_riddim
                )
                
                result["midi_file_path"] = midi_path
                result["midi_file_url"] = f"/api/v1/analysis/download/midi/{job_id}"
            
            # Complete job
            job_data["status"] = "completed"
            job_data["message"] = "Analysis completed successfully"
            job_data["progress"] = 1.0
            job_data["result"] = result
            job_data["updated_at"] = datetime.now()
            
        finally:
            # Clean up temporary file
            Path(tmp_file_path).unlink(missing_ok=True)
            
    except Exception as e:
        logger.error(f"Analysis job {job_id} failed: {e}")
        job_data["status"] = "failed"
        job_data["message"] = f"Analysis failed: {str(e)}"
        job_data["error"] = str(e)
        job_data["updated_at"] = datetime.now()


async def _process_batch_analysis(
    batch_job_id: str,
    files: List[UploadFile],
    job_name: str,
    include_midi: bool,
    riddim_type: Optional[str],
    instruments: Optional[List[str]]
):
    """Process batch analysis in background."""
    batch_job_data = analysis_jobs[batch_job_id]
    
    try:
        batch_job_data["status"] = "processing"
        batch_job_data["message"] = f"Processing batch: {job_name}"
        
        file_results = []
        completed = 0
        failed = 0
        
        for i, file in enumerate(files):
            try:
                # Create individual job
                file_job_id = f"{batch_job_id}_file_{i}"
                
                # Process file
                await _process_analysis(
                    file_job_id,
                    file,
                    include_midi,
                    riddim_type,
                    instruments
                )
                
                # Get result
                if file_job_id in analysis_jobs:
                    file_job = analysis_jobs[file_job_id]
                    if file_job["status"] == "completed":
                        completed += 1
                        file_results.append({
                            "file_name": file.filename,
                            "status": "completed",
                            "result": file_job["result"]
                        })
                    else:
                        failed += 1
                        file_results.append({
                            "file_name": file.filename,
                            "status": "failed",
                            "error": file_job.get("error", "Unknown error")
                        })
                
                # Update batch progress
                progress = (i + 1) / len(files)
                batch_job_data["progress"] = progress
                batch_job_data["completed_files"] = completed
                batch_job_data["failed_files"] = failed
                batch_job_data["updated_at"] = datetime.now()
                
            except Exception as e:
                logger.error(f"Batch file processing failed for {file.filename}: {e}")
                failed += 1
                file_results.append({
                    "file_name": file.filename,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Complete batch job
        batch_job_data["status"] = "completed"
        batch_job_data["message"] = f"Batch completed: {completed} successful, {failed} failed"
        batch_job_data["progress"] = 1.0
        batch_job_data["result"] = {
            "job_name": job_name,
            "total_files": len(files),
            "completed_files": completed,
            "failed_files": failed,
            "file_results": file_results
        }
        batch_job_data["updated_at"] = datetime.now()
        
    except Exception as e:
        logger.error(f"Batch job {batch_job_id} failed: {e}")
        batch_job_data["status"] = "failed"
        batch_job_data["message"] = f"Batch processing failed: {str(e)}"
        batch_job_data["error"] = str(e)
        batch_job_data["updated_at"] = datetime.now()