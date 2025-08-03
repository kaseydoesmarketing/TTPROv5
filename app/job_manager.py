"""
Robust Background Job Manager
Handles job persistence, recovery, and monitoring with comprehensive error handling
"""

import logging
import time
import json
import traceback
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from contextlib import contextmanager

import redis
from celery import Celery
from celery.exceptions import Retry, WorkerLostError
from sqlalchemy.orm import Session

from .config import settings
from .database_manager import db_manager

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"

class JobPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class JobMetadata:
    """Metadata for tracking job execution"""
    job_id: str
    task_name: str
    status: JobStatus
    priority: JobPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    progress: float = 0.0
    user_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class RobustJobManager:
    """Enhanced job manager with persistence and recovery"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.celery_app: Optional[Celery] = None
        self.connection_healthy = False
        self.job_metadata_key = "ttpr:jobs"
        self.dead_letter_key = "ttpr:failed_jobs"
        
    def initialize(self) -> bool:
        """Initialize job manager with Redis and Celery"""
        try:
            # Initialize Redis connection
            if not self._init_redis():
                logger.error("❌ Failed to initialize Redis connection")
                return False
            
            # Initialize Celery
            if not self._init_celery():
                logger.error("❌ Failed to initialize Celery")
                return False
            
            logger.info("✅ Job manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Job manager initialization failed: {e}")
            return False
    
    def _init_redis(self) -> bool:
        """Initialize Redis connection with error handling"""
        try:
            redis_url = settings.redis_url
            if not redis_url:
                logger.warning("⚠️ REDIS_URL not configured, using fallback")
                redis_url = "redis://localhost:6379/0"
            
            self.redis_client = redis.from_url(
                redis_url,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            self.connection_healthy = True
            logger.info("✅ Redis connection established")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            self.connection_healthy = False
            return False
    
    def _init_celery(self) -> bool:
        """Initialize Celery with robust configuration"""
        try:
            self.celery_app = Celery(
                "titletesterpro_robust",
                broker=settings.redis_url or "redis://localhost:6379/0",
                backend=settings.redis_url or "redis://localhost:6379/0",
                include=["app.robust_tasks"]
            )
            
            # Enhanced Celery configuration
            self.celery_app.conf.update(
                # Serialization
                task_serializer="json",
                accept_content=["json"],
                result_serializer="json",
                
                # Timezone
                timezone="UTC",
                enable_utc=True,
                
                # Task execution
                task_track_started=True,
                task_time_limit=30 * 60,  # 30 minutes
                task_soft_time_limit=25 * 60,  # 25 minutes
                task_acks_late=True,
                task_reject_on_worker_lost=True,
                
                # Worker configuration
                worker_prefetch_multiplier=1,
                worker_max_tasks_per_child=100,
                worker_disable_rate_limits=False,
                
                # Retry configuration
                task_default_retry_delay=60,  # 1 minute
                task_max_retries=3,
                
                # Result backend
                result_expires=3600,  # 1 hour
                result_persistent=True,
                
                # Broker configuration
                broker_connection_retry_on_startup=True,
                broker_connection_retry=True,
                broker_connection_max_retries=10,
                
                # Monitoring
                worker_send_task_events=True,
                task_send_sent_event=True
            )
            
            # Job schedule with error recovery
            self.celery_app.conf.beat_schedule = {
                "rotate-titles-robust": {
                    "task": "app.robust_tasks.rotate_titles_robust",
                    "schedule": 60.0,  # Every minute
                    "options": {"priority": JobPriority.HIGH.value}
                },
                "cleanup-completed-tests-robust": {
                    "task": "app.robust_tasks.cleanup_completed_tests_robust", 
                    "schedule": 3600.0,  # Every hour
                    "options": {"priority": JobPriority.NORMAL.value}
                },
                "recover-failed-jobs": {
                    "task": "app.robust_tasks.recover_failed_jobs",
                    "schedule": 300.0,  # Every 5 minutes
                    "options": {"priority": JobPriority.HIGH.value}
                },
                "cleanup-old-job-metadata": {
                    "task": "app.robust_tasks.cleanup_old_job_metadata",
                    "schedule": 86400.0,  # Daily
                    "options": {"priority": JobPriority.LOW.value}
                }
            }
            
            logger.info("✅ Celery configuration completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Celery initialization failed: {e}")
            return False
    
    def submit_job(self, task_name: str, args: List[Any] = None, kwargs: Dict[str, Any] = None,
                   priority: JobPriority = JobPriority.NORMAL, user_id: Optional[str] = None,
                   delay: Optional[float] = None) -> Optional[str]:
        """Submit a job with metadata tracking"""
        try:
            if not self.celery_app:
                logger.error("❌ Celery not initialized")
                return None
            
            job_id = f"job_{int(time.time() * 1000)}_{hash(task_name + str(args))}"
            
            # Create job metadata
            metadata = JobMetadata(
                job_id=job_id,
                task_name=task_name,
                status=JobStatus.PENDING,
                priority=priority,
                created_at=datetime.utcnow(),
                user_id=user_id
            )
            
            # Store metadata
            self._store_job_metadata(metadata)
            
            # Submit job to Celery
            task_kwargs = kwargs or {}
            task_kwargs['job_id'] = job_id
            
            if delay:
                result = self.celery_app.send_task(
                    task_name,
                    args=args or [],
                    kwargs=task_kwargs,
                    countdown=delay,
                    priority=priority.value,
                    task_id=job_id
                )
            else:
                result = self.celery_app.send_task(
                    task_name,
                    args=args or [],
                    kwargs=task_kwargs,
                    priority=priority.value,
                    task_id=job_id
                )
            
            logger.info(f"✅ Job {job_id} submitted: {task_name}")
            return job_id
            
        except Exception as e:
            logger.error(f"❌ Job submission failed: {e}")
            return None
    
    def _store_job_metadata(self, metadata: JobMetadata):
        """Store job metadata in Redis"""
        try:
            if self.redis_client and self.connection_healthy:
                key = f"{self.job_metadata_key}:{metadata.job_id}"
                data = asdict(metadata)
                
                # Convert datetime objects to ISO strings
                for field in ['created_at', 'started_at', 'completed_at']:
                    if data[field]:
                        data[field] = data[field].isoformat()
                
                # Convert enum to value
                data['status'] = data['status'].value
                data['priority'] = data['priority'].value
                
                self.redis_client.setex(key, 86400 * 7, json.dumps(data))  # 7 days TTL
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to store job metadata: {e}")
    
    def get_job_status(self, job_id: str) -> Optional[JobMetadata]:
        """Get job status and metadata"""
        try:
            if not self.redis_client or not self.connection_healthy:
                return None
            
            key = f"{self.job_metadata_key}:{job_id}"
            data = self.redis_client.get(key)
            
            if not data:
                return None
            
            job_data = json.loads(data)
            
            # Convert back from stored format
            for field in ['created_at', 'started_at', 'completed_at']:
                if job_data[field]:
                    job_data[field] = datetime.fromisoformat(job_data[field])
            
            job_data['status'] = JobStatus(job_data['status'])
            job_data['priority'] = JobPriority(job_data['priority'])
            
            return JobMetadata(**job_data)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get job status: {e}")
            return None
    
    def update_job_status(self, job_id: str, status: JobStatus, 
                         error_message: Optional[str] = None,
                         progress: Optional[float] = None,
                         result: Optional[Dict[str, Any]] = None):
        """Update job status and metadata"""
        try:
            metadata = self.get_job_status(job_id)
            if not metadata:
                logger.warning(f"⚠️ Job metadata not found: {job_id}")
                return
            
            # Update fields
            metadata.status = status
            if error_message:
                metadata.error_message = error_message
            if progress is not None:
                metadata.progress = progress
            if result is not None:
                metadata.result = result
            
            # Update timestamps
            if status == JobStatus.RUNNING and not metadata.started_at:
                metadata.started_at = datetime.utcnow()
            elif status in [JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED]:
                metadata.completed_at = datetime.utcnow()
            
            self._store_job_metadata(metadata)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to update job status: {e}")
    
    def retry_job(self, job_id: str) -> bool:
        """Retry a failed job"""
        try:
            metadata = self.get_job_status(job_id)
            if not metadata:
                return False
            
            if metadata.retry_count >= metadata.max_retries:
                logger.warning(f"⚠️ Job {job_id} exceeded max retries")
                self._move_to_dead_letter(metadata)
                return False
            
            # Increment retry count
            metadata.retry_count += 1
            metadata.status = JobStatus.RETRY
            self._store_job_metadata(metadata)
            
            # Resubmit job
            new_job_id = self.submit_job(
                metadata.task_name,
                priority=metadata.priority,
                user_id=metadata.user_id
            )
            
            logger.info(f"🔄 Job {job_id} retried as {new_job_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Job retry failed: {e}")
            return False
    
    def _move_to_dead_letter(self, metadata: JobMetadata):
        """Move failed job to dead letter queue"""
        try:
            if self.redis_client and self.connection_healthy:
                dead_letter_data = asdict(metadata)
                dead_letter_data['moved_to_dlq_at'] = datetime.utcnow().isoformat()
                
                self.redis_client.lpush(
                    self.dead_letter_key,
                    json.dumps(dead_letter_data)
                )
                
                logger.warning(f"📮 Job {metadata.job_id} moved to dead letter queue")
                
        except Exception as e:
            logger.error(f"❌ Failed to move job to dead letter queue: {e}")
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """Get job queue statistics"""
        try:
            stats = {
                "redis_healthy": self.connection_healthy,
                "celery_initialized": self.celery_app is not None,
                "active_jobs": 0,
                "pending_jobs": 0,
                "failed_jobs": 0,
                "completed_jobs": 0
            }
            
            if self.redis_client and self.connection_healthy:
                # Get job counts by status
                pattern = f"{self.job_metadata_key}:*"
                for key in self.redis_client.scan_iter(match=pattern):
                    try:
                        data = json.loads(self.redis_client.get(key))
                        status = data.get('status', 'unknown')
                        
                        if status == 'running':
                            stats['active_jobs'] += 1
                        elif status == 'pending':
                            stats['pending_jobs'] += 1
                        elif status == 'failed':
                            stats['failed_jobs'] += 1
                        elif status == 'success':
                            stats['completed_jobs'] += 1
                    except:
                        continue
                
                # Dead letter queue count
                stats['dead_letter_count'] = self.redis_client.llen(self.dead_letter_key)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get job statistics: {e}")
            return {"error": str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get job manager health status"""
        return {
            "redis_connected": self.connection_healthy,
            "celery_configured": self.celery_app is not None,
            "status": "healthy" if (self.connection_healthy and self.celery_app) else "degraded",
            "statistics": self.get_job_statistics()
        }

# Global job manager instance
job_manager = RobustJobManager()

def robust_task(max_retries: int = 3, retry_delay: float = 60.0):
    """Decorator for creating robust Celery tasks with automatic metadata tracking"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            job_id = kwargs.pop('job_id', None)
            
            try:
                # Update job status to running
                if job_id:
                    job_manager.update_job_status(job_id, JobStatus.RUNNING)
                
                # Execute the task
                result = func(*args, **kwargs)
                
                # Update job status to success
                if job_id:
                    job_manager.update_job_status(job_id, JobStatus.SUCCESS, result=result)
                
                return result
                
            except Exception as e:
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                logger.error(f"❌ Task failed: {error_msg}")
                
                # Update job status to failed
                if job_id:
                    job_manager.update_job_status(job_id, JobStatus.FAILED, error_message=error_msg)
                
                raise
        
        return wrapper
    return decorator

@contextmanager
def get_database_session():
    """Context manager for database sessions in background tasks"""
    session = None
    try:
        session = db_manager.get_session_with_retry()
        if not session:
            raise Exception("Failed to get database session")
        yield session
        session.commit()
    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"❌ Database session error in background task: {e}")
        raise
    finally:
        if session:
            session.close()

def initialize_job_manager() -> bool:
    """Initialize the job manager"""
    return job_manager.initialize()