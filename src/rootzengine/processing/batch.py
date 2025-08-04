"""Batch processing system for audio files."""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from rootzengine.audio.analysis import AudioStructureAnalyzer
from rootzengine.storage.interface import StorageManager
from rootzengine.core.config import settings

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingJob:
    """Represents a processing job."""
    id: str
    file_path: str
    status: JobStatus = JobStatus.PENDING
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None
    result: Optional[Dict] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class BatchProcessor:
    """Batch processor for audio files."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.jobs: Dict[str, ProcessingJob] = {}
        self.storage = StorageManager()
        self.analyzer = AudioStructureAnalyzer()
        self._job_counter = 0
    
    def add_job(self, file_path: str) -> str:
        """Add a processing job to the queue."""
        self._job_counter += 1
        job_id = f"job_{self._job_counter}_{int(time.time())}"
        
        job = ProcessingJob(
            id=job_id,
            file_path=file_path
        )
        
        self.jobs[job_id] = job
        logger.info(f"Added job {job_id} for file {file_path}")
        return job_id
    
    def add_jobs(self, file_paths: List[str]) -> List[str]:
        """Add multiple processing jobs."""
        job_ids = []
        for file_path in file_paths:
            job_id = self.add_job(file_path)
            job_ids.append(job_id)
        return job_ids
    
    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """Get a job by ID."""
        return self.jobs.get(job_id)
    
    def get_pending_jobs(self) -> List[ProcessingJob]:
        """Get all pending jobs."""
        return [job for job in self.jobs.values() if job.status == JobStatus.PENDING]
    
    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get job status."""
        job = self.jobs.get(job_id)
        return job.status if job else None
    
    def process_job(self, job: ProcessingJob) -> ProcessingJob:
        """Process a single job."""
        logger.info(f"Starting job {job.id} for file {job.file_path}")
        
        job.status = JobStatus.RUNNING
        job.started_at = time.time()
        
        try:
            # Check if file exists
            if not Path(job.file_path).exists():
                raise FileNotFoundError(f"File not found: {job.file_path}")
            
            # Analyze the file
            result = self.analyzer.analyze_structure(
                job.file_path, 
                perform_separation=False
            )
            
            # Save result to storage
            filename = Path(job.file_path).name
            self.storage.save_analysis_result(filename, result)
            
            # Update job
            job.result = result
            job.status = JobStatus.COMPLETED
            job.completed_at = time.time()
            
            logger.info(f"Completed job {job.id} in {job.completed_at - job.started_at:.2f}s")
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = time.time()
            
            logger.error(f"Job {job.id} failed: {e}")
        
        return job
    
    def process_batch(self, job_ids: Optional[List[str]] = None) -> Dict[str, ProcessingJob]:
        """Process a batch of jobs in parallel."""
        if job_ids is None:
            jobs_to_process = self.get_pending_jobs()
        else:
            jobs_to_process = [self.jobs[jid] for jid in job_ids if jid in self.jobs]
        
        if not jobs_to_process:
            logger.info("No jobs to process")
            return {}
        
        logger.info(f"Processing {len(jobs_to_process)} jobs with {self.max_workers} workers")
        
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            future_to_job = {
                executor.submit(self.process_job, job): job 
                for job in jobs_to_process
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_job):
                job = future_to_job[future]
                try:
                    completed_job = future.result()
                    results[completed_job.id] = completed_job
                except Exception as e:
                    logger.error(f"Job {job.id} raised an exception: {e}")
                    job.status = JobStatus.FAILED
                    job.error = str(e)
                    results[job.id] = job
        
        return results
    
    def process_all_pending(self) -> Dict[str, ProcessingJob]:
        """Process all pending jobs."""
        return self.process_batch()
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        stats = {
            "total": len(self.jobs),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0
        }
        
        for job in self.jobs.values():
            stats[job.status.value] += 1
        
        return stats
    
    def clear_completed_jobs(self) -> int:
        """Clear completed and failed jobs."""
        to_remove = [
            job_id for job_id, job in self.jobs.items() 
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]
        ]
        
        for job_id in to_remove:
            del self.jobs[job_id]
        
        logger.info(f"Cleared {len(to_remove)} completed/failed jobs")
        return len(to_remove)


class FileProcessor:
    """High-level file processor with directory scanning."""
    
    def __init__(self, max_workers: int = 4):
        self.batch_processor = BatchProcessor(max_workers)
        self.supported_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[str]:
        """Scan directory for audio files."""
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        audio_files = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                audio_files.append(str(file_path))
        
        logger.info(f"Found {len(audio_files)} audio files in {directory}")
        return audio_files
    
    def process_directory(self, directory: str, recursive: bool = True) -> Dict[str, ProcessingJob]:
        """Process all audio files in a directory."""
        audio_files = self.scan_directory(directory, recursive)
        
        if not audio_files:
            logger.info(f"No audio files found in {directory}")
            return {}
        
        # Add jobs for all files
        job_ids = self.batch_processor.add_jobs(audio_files)
        
        # Process the batch
        return self.batch_processor.process_batch(job_ids)
    
    def process_files(self, file_paths: List[str]) -> Dict[str, ProcessingJob]:
        """Process specific files."""
        job_ids = self.batch_processor.add_jobs(file_paths)
        return self.batch_processor.process_batch(job_ids)
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self.batch_processor.get_stats()


def create_progress_callback(total_jobs: int) -> Callable[[ProcessingJob], None]:
    """Create a progress callback function."""
    completed = {"count": 0}
    
    def callback(job: ProcessingJob):
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            completed["count"] += 1
            progress = (completed["count"] / total_jobs) * 100
            status_emoji = "✅" if job.status == JobStatus.COMPLETED else "❌"
            logger.info(f"{status_emoji} {job.id}: {progress:.1f}% complete ({completed['count']}/{total_jobs})")
    
    return callback