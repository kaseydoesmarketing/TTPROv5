from celery import Celery
import os
"""
Robust background tasks with comprehensive error handling and recovery
All tasks use the enhanced job manager for reliability
"""

import logging
import asyncio
import time
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta

from celery import current_app
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from .job_manager import robust_task, get_database_session, job_manager, JobStatus
from .models import ABTest, TitleRotation, QuotaUsage, User
from .youtube_api import YouTubeAPIClient
from .database_manager import retry_on_database_error

logger = logging.getLogger(__name__)

@current_app.task(bind=True)
@robust_task(max_retries=3, retry_delay=60.0)
def rotate_titles_robust(self, job_id: str = None):
    """Robust title rotation with comprehensive error handling"""
    logger.info(f"🔄 Starting robust title rotation job {job_id}")
    
    try:
        with get_database_session() as db:
            active_tests = _get_active_tests_safely(db)
            
            if not active_tests:
                logger.info("No active tests found for rotation")
                return {"rotated_count": 0, "message": "No active tests"}
            
            rotation_results = []
            successful_rotations = 0
            
            for test in active_tests:
                try:
                    if job_id:
                        progress = successful_rotations / len(active_tests)
                        job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=progress)
                    
                    result = _perform_robust_title_rotation(db, test)
                    rotation_results.append({
                        "test_id": test.id,
                        "status": "success" if result else "skipped",
                        "result": result
                    })
                    
                    if result:
                        successful_rotations += 1
                        
                except Exception as e:
                    logger.error(f"❌ Rotation failed for test {test.id}: {e}")
                    rotation_results.append({
                        "test_id": test.id,
                        "status": "error",
                        "error": str(e)
                    })
            
            db.commit()
            
            result_summary = {
                "total_tests": len(active_tests),
                "successful_rotations": successful_rotations,
                "results": rotation_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Title rotation completed: {successful_rotations}/{len(active_tests)} successful")
            return result_summary
            
    except Exception as e:
        logger.error(f"❌ Title rotation job failed: {e}")
        raise

@retry_on_database_error(max_retries=3)
def _get_active_tests_safely(db: Session) -> List[ABTest]:
    """Safely get active tests with database retry logic"""
    return db.query(ABTest).filter(
        ABTest.status == "active",
        ABTest.started_at.isnot(None)
    ).all()

def _perform_robust_title_rotation(db: Session, test: ABTest) -> Dict[str, Any]:
    """Perform title rotation with comprehensive error handling"""
    try:
        # Check if rotation is due
        if not _is_rotation_due(db, test):
            return None
        
        # Get user and validate tokens
        user = db.query(User).filter(User.id == test.user_id).first()
        if not user:
            logger.error(f"User not found for test {test.id}")
            return None
        
        access_token = user.get_google_access_token()
        if not access_token:
            logger.error(f"No access token for user {user.id}")
            # Try to refresh tokens
            if not _attempt_token_refresh(db, user):
                return None
            access_token = user.get_google_access_token()
        
        # Get current rotation and update metrics
        current_rotation = db.query(TitleRotation).filter(
            TitleRotation.ab_test_id == test.id,
            TitleRotation.ended_at.is_(None)
        ).first()
        
        if current_rotation:
            _finalize_current_rotation(current_rotation, test, access_token, user.id)
        
        # Perform the rotation
        next_variant_index = (test.current_variant_index + 1) % len(test.title_variants)
        new_title = test.title_variants[next_variant_index]
        
        # Update video title with retry logic
        if not _update_video_title_with_retry(test.video_id, new_title, access_token):
            logger.error(f"Failed to update video title for test {test.id}")
            return None
        
        # Update quota usage
        _update_quota_usage_safely(user.id, "videos_update", 50)
        
        # Update test variant index
        test.current_variant_index = next_variant_index
        
        # Create new rotation record
        new_rotation = _create_new_rotation_record(test, next_variant_index, new_title, access_token, user.id)
        if new_rotation:
            db.add(new_rotation)
        
        logger.info(f"✅ Rotated title for test {test.id} to variant {next_variant_index}: '{new_title}'")
        
        return {
            "test_id": test.id,
            "new_variant_index": next_variant_index,
            "new_title": new_title,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Title rotation failed for test {test.id}: {e}")
        raise

def _is_rotation_due(db: Session, test: ABTest) -> bool:
    """Check if a rotation is due for the test"""
    try:
        last_rotation = db.query(TitleRotation).filter(
            TitleRotation.ab_test_id == test.id
        ).order_by(TitleRotation.started_at.desc()).first()
        
        if not last_rotation:
            return True
        
        time_since_rotation = datetime.utcnow() - last_rotation.started_at
        return time_since_rotation.total_seconds() >= (test.rotation_interval_hours * 3600)
        
    except Exception as e:
        logger.error(f"❌ Error checking rotation due: {e}")
        return False

def _attempt_token_refresh(db: Session, user: User) -> bool:
    """Attempt to refresh user's Google tokens"""
    try:
        from .auth_manager import auth_manager
        
        refresh_token = user.get_google_refresh_token()
        if not refresh_token:
            logger.error(f"No refresh token for user {user.id}")
            return False
        
        new_tokens = auth_manager.refresh_google_token(refresh_token)
        user.set_google_tokens(
            access_token=new_tokens.get("access_token"),
            refresh_token=new_tokens.get("refresh_token", refresh_token)
        )
        db.commit()
        
        logger.info(f"✅ Refreshed tokens for user {user.id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Token refresh failed for user {user.id}: {e}")
        return False

def _finalize_current_rotation(rotation: TitleRotation, test: ABTest, access_token: str, user_id: str):
    """Finalize the current rotation with end metrics"""
    try:
        youtube_client = YouTubeAPIClient()
        
        start_date = rotation.started_at.strftime('%Y-%m-%d')
        end_date = datetime.utcnow().strftime('%Y-%m-%d')
        
        video_analytics = asyncio.run(youtube_client.get_video_analytics(
            test.video_id, start_date, end_date, access_token
        ))
        
        rotation.views_end = video_analytics.get('views', 0)
        rotation.likes_end = video_analytics.get('likes', 0)
        rotation.comments_end = video_analytics.get('comments', 0)
        
        if rotation.views_start is not None:
            rotation.views_gained = max(0, rotation.views_end - rotation.views_start)
        
        if rotation.views_end > 0 and rotation.likes_end is not None:
            rotation.engagement_rate = (rotation.likes_end / rotation.views_end) * 100
        
        rotation.ended_at = datetime.utcnow()
        
        _update_quota_usage_safely(user_id, "video_analytics", 1)
        
    except Exception as e:
        logger.error(f"❌ Error finalizing rotation {rotation.id}: {e}")
        rotation.ended_at = datetime.utcnow()

def _update_video_title_with_retry(video_id: str, new_title: str, access_token: str, max_retries: int = 3) -> bool:
    """Update video title with retry logic"""
    youtube_client = YouTubeAPIClient()
    
    for attempt in range(max_retries):
        try:
            success = asyncio.run(youtube_client.update_video_title(
                video_id, new_title, access_token
            ))
            
            if success:
                return True
            
            logger.warning(f"⚠️ Video title update attempt {attempt + 1} failed")
            
        except Exception as e:
            logger.error(f"❌ Video title update attempt {attempt + 1} error: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return False

def _create_new_rotation_record(test: ABTest, variant_index: int, title: str, access_token: str, user_id: str) -> TitleRotation:
    """Create new rotation record with start metrics"""
    try:
        youtube_client = YouTubeAPIClient()
        current_date = datetime.utcnow().strftime('%Y-%m-%d')
        
        video_analytics = asyncio.run(youtube_client.get_video_analytics(
            test.video_id, current_date, current_date, access_token
        ))
        
        new_rotation = TitleRotation(
            ab_test_id=test.id,
            variant_index=variant_index,
            title=title,
            started_at=datetime.utcnow(),
            views_start=video_analytics.get('views', 0),
            likes_start=video_analytics.get('likes', 0),
            comments_start=video_analytics.get('comments', 0)
        )
        
        _update_quota_usage_safely(user_id, "video_analytics", 1)
        
        return new_rotation
        
    except Exception as e:
        logger.error(f"❌ Error creating rotation record: {e}")
        # Return basic rotation record without metrics
        return TitleRotation(
            ab_test_id=test.id,
            variant_index=variant_index,
            title=title,
            started_at=datetime.utcnow()
        )

def _update_quota_usage_safely(user_id: str, api_call_type: str, quota_units: int):
    """Update quota usage with error handling"""
    try:
        # Submit as a separate job to avoid blocking main task
        job_manager.submit_job(
            "app.robust_tasks.update_quota_usage_robust",
            args=[user_id, api_call_type, quota_units],
            priority=job_manager.JobPriority.LOW
        )
    except Exception as e:
        logger.warning(f"⚠️ Failed to submit quota update job: {e}")

@current_app.task(bind=True)
@robust_task(max_retries=3, retry_delay=30.0)
def cleanup_completed_tests_robust(self, job_id: str = None):
    """Robust cleanup of completed tests"""
    logger.info(f"🧹 Starting robust test cleanup job {job_id}")
    
    try:
        with get_database_session() as db:
            now = datetime.utcnow()
            
            tests_to_complete = db.query(ABTest).filter(
                ABTest.status == "active",
                ABTest.started_at.isnot(None)
            ).all()
            
            completed_count = 0
            
            for test in tests_to_complete:
                try:
                    time_running = now - test.started_at
                    if time_running.total_seconds() >= (test.test_duration_hours * 3600):
                        
                        # Finalize current rotation
                        current_rotation = db.query(TitleRotation).filter(
                            TitleRotation.ab_test_id == test.id,
                            TitleRotation.ended_at.is_(None)
                        ).first()
                        
                        if current_rotation:
                            current_rotation.ended_at = now
                        
                        # Mark test as completed
                        test.status = "completed"
                        test.completed_at = now
                        completed_count += 1
                        
                        logger.info(f"✅ Completed test {test.id}")
                        
                except Exception as e:
                    logger.error(f"❌ Error completing test {test.id}: {e}")
            
            db.commit()
            
            result = {
                "completed_count": completed_count,
                "total_checked": len(tests_to_complete),
                "timestamp": now.isoformat()
            }
            
            logger.info(f"✅ Test cleanup completed: {completed_count} tests completed")
            return result
            
    except Exception as e:
        logger.error(f"❌ Test cleanup job failed: {e}")
        raise

@current_app.task(bind=True)
@robust_task(max_retries=2, retry_delay=60.0)
def update_quota_usage_robust(self, user_id: str, api_call_type: str, quota_units: int, job_id: str = None):
    """Robust quota usage update"""
    try:
        with get_database_session() as db:
            today = datetime.utcnow().date()
            
            quota_record = db.query(QuotaUsage).filter(
                QuotaUsage.user_id == user_id,
                QuotaUsage.date >= today,
                QuotaUsage.date < today + timedelta(days=1)
            ).first()
            
            if not quota_record:
                quota_record = QuotaUsage(
                    user_id=user_id,
                    date=datetime.utcnow(),
                    api_calls_count=0,
                    quota_units_used=0,
                    videos_list_calls=0,
                    videos_update_calls=0
                )
                db.add(quota_record)
            
            quota_record.api_calls_count = (quota_record.api_calls_count or 0) + 1
            quota_record.quota_units_used = (quota_record.quota_units_used or 0) + quota_units
            
            if api_call_type == "videos_list":
                quota_record.videos_list_calls = (quota_record.videos_list_calls or 0) + 1
            elif api_call_type == "videos_update":
                quota_record.videos_update_calls = (quota_record.videos_update_calls or 0) + 1
            
            db.commit()
            
            logger.info(f"✅ Updated quota usage for user {user_id}: +{quota_units} units")
            return {"user_id": user_id, "quota_units": quota_units, "api_call_type": api_call_type}
            
    except Exception as e:
        logger.error(f"❌ Quota usage update failed: {e}")
        raise

@current_app.task(bind=True)
@robust_task(max_retries=2, retry_delay=120.0)
def recover_failed_jobs(self, job_id: str = None):
    """Recover jobs that failed due to transient issues"""
    logger.info(f"🔧 Starting job recovery task {job_id}")
    
    try:
        stats = job_manager.get_job_statistics()
        recovery_count = 0
        
        # Logic to identify and retry failed jobs would go here
        # For now, just return statistics
        
        result = {
            "recovery_count": recovery_count,
            "job_statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Job recovery completed: {recovery_count} jobs recovered")
        return result
        
    except Exception as e:
        logger.error(f"❌ Job recovery failed: {e}")
        raise

@current_app.task(bind=True) 
@robust_task(max_retries=1, retry_delay=300.0)
def cleanup_old_job_metadata(self, job_id: str = None):
    """Clean up old job metadata from Redis"""
    logger.info(f"🧹 Starting job metadata cleanup {job_id}")
    
    try:
        if not job_manager.redis_client or not job_manager.connection_healthy:
            logger.warning("⚠️ Redis not available for cleanup")
            return {"status": "skipped", "reason": "redis_unavailable"}
        
        # Clean up job metadata older than 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        cleaned_count = 0
        
        pattern = f"{job_manager.job_metadata_key}:*"
        for key in job_manager.redis_client.scan_iter(match=pattern):
            try:
                data = job_manager.redis_client.get(key)
                if data:
                    job_data = json.loads(data)
                    created_at = datetime.fromisoformat(job_data.get('created_at', ''))
                    
                    if created_at < cutoff_date:
                        job_manager.redis_client.delete(key)
                        cleaned_count += 1
                        
            except Exception as e:
                logger.warning(f"⚠️ Error processing job metadata key {key}: {e}")
        
        result = {
            "cleaned_count": cleaned_count,
            "cutoff_date": cutoff_date.isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Job metadata cleanup completed: {cleaned_count} entries removed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Job metadata cleanup failed: {e}")
        raise

redis_url = os.getenv('REDIS_URL', '')
try:
    app_celery
except NameError:
    app_celery = Celery('ttpro', broker=redis_url, backend=redis_url)
