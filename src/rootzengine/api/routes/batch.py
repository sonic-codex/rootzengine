"""API routes for batch processing functionality."""

from typing import List, Optional
from fastapi import APIRouter, Form, status
from fastapi.responses import JSONResponse

from rootzengine.processing.batch import FileProcessor, JobStatus
from rootzengine.core.config import settings

router = APIRouter()

# Global file processor instance
file_processor = FileProcessor(max_workers=4)


@router.post("/process-directory")
async def process_directory(
    directory: str = Form(...),
    recursive: bool = Form(True),
) -> JSONResponse:
    """Process all audio files in a directory."""
    try:
        # Scan directory first
        audio_files = file_processor.scan_directory(directory, recursive)
        
        if not audio_files:
            return JSONResponse(
                content={
                    "message": f"No audio files found in {directory}",
                    "files_found": 0
                },
                status_code=status.HTTP_200_OK,
            )
        
        # Process the directory
        results = file_processor.process_directory(directory, recursive)
        
        # Calculate stats
        completed = sum(1 for job in results.values() if job.status == JobStatus.COMPLETED)
        failed = sum(1 for job in results.values() if job.status == JobStatus.FAILED)
        
        return JSONResponse(
            content={
                "message": f"Processed {len(audio_files)} files from {directory}",
                "directory": directory,
                "recursive": recursive,
                "files_found": len(audio_files),
                "jobs_created": len(results),
                "completed": completed,
                "failed": failed,
                "results": {
                    job_id: {
                        "file_path": job.file_path,
                        "status": job.status.value,
                        "error": job.error
                    }
                    for job_id, job in results.items()
                }
            },
            status_code=status.HTTP_200_OK,
        )
        
    except FileNotFoundError as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/process-files")
async def process_files(
    file_paths: List[str] = Form(...),
) -> JSONResponse:
    """Process specific audio files."""
    try:
        # Process the files
        results = file_processor.process_files(file_paths)
        
        # Calculate stats
        completed = sum(1 for job in results.values() if job.status == JobStatus.COMPLETED)
        failed = sum(1 for job in results.values() if job.status == JobStatus.FAILED)
        
        return JSONResponse(
            content={
                "message": f"Processed {len(file_paths)} files",
                "files_submitted": len(file_paths),
                "jobs_created": len(results),
                "completed": completed,
                "failed": failed,
                "results": {
                    job_id: {
                        "file_path": job.file_path,
                        "status": job.status.value,
                        "error": job.error
                    }
                    for job_id, job in results.items()
                }
            },
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/jobs")
async def list_jobs() -> JSONResponse:
    """List all processing jobs."""
    try:
        jobs = file_processor.batch_processor.jobs
        
        return JSONResponse(
            content={
                "jobs": {
                    job_id: {
                        "id": job.id,
                        "file_path": job.file_path,
                        "status": job.status.value,
                        "created_at": job.created_at,
                        "started_at": job.started_at,
                        "completed_at": job.completed_at,
                        "error": job.error
                    }
                    for job_id, job in jobs.items()
                },
                "count": len(jobs)
            },
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> JSONResponse:
    """Get a specific job by ID."""
    try:
        job = file_processor.batch_processor.get_job(job_id)
        
        if job is None:
            return JSONResponse(
                content={"error": f"Job {job_id} not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        return JSONResponse(
            content={
                "job": {
                    "id": job.id,
                    "file_path": job.file_path,
                    "status": job.status.value,
                    "created_at": job.created_at,
                    "started_at": job.started_at,
                    "completed_at": job.completed_at,
                    "error": job.error,
                    "result": job.result
                }
            },
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/stats")
async def get_stats() -> JSONResponse:
    """Get processing statistics."""
    try:
        stats = file_processor.get_stats()
        
        return JSONResponse(
            content=stats,
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.delete("/jobs/completed")
async def clear_completed_jobs() -> JSONResponse:
    """Clear completed and failed jobs."""
    try:
        cleared_count = file_processor.batch_processor.clear_completed_jobs()
        
        return JSONResponse(
            content={
                "message": f"Cleared {cleared_count} completed/failed jobs",
                "cleared_count": cleared_count
            },
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/scan-directory")
async def scan_directory(
    directory: str = Form(...),
    recursive: bool = Form(True),
) -> JSONResponse:
    """Scan directory for audio files without processing them."""
    try:
        audio_files = file_processor.scan_directory(directory, recursive)
        
        return JSONResponse(
            content={
                "directory": directory,
                "recursive": recursive,
                "files_found": len(audio_files),
                "files": audio_files
            },
            status_code=status.HTTP_200_OK,
        )
        
    except FileNotFoundError as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )