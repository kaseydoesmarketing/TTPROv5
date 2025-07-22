from celery import current_app
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import ABTest, TitleRotation, QuotaUsage, User
from .youtube_api import YouTubeAPIClient
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)


@current_app.task
def rotate_titles():
    """Check for A/B tests that need title rotation"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        active_tests = db.query(ABTest).filter(
            ABTest.status == "active",
            ABTest.started_at.isnot(None)
        ).all()
        
        for test in active_tests:
            last_rotation = db.query(TitleRotation).filter(
                TitleRotation.ab_test_id == test.id
            ).order_by(TitleRotation.started_at.desc()).first()
            
            if last_rotation:
                time_since_rotation = now - last_rotation.started_at
                if time_since_rotation.total_seconds() >= (test.rotation_interval_hours * 3600):
                    _perform_title_rotation(db, test)
            else:
                _perform_title_rotation(db, test)
                
        db.commit()
        logger.info(f"Title rotation check completed for {len(active_tests)} active tests")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in rotate_titles task: {str(e)}")
        raise
    finally:
        db.close()


def _perform_title_rotation(db: Session, test: ABTest):
    """Perform the actual title rotation for a test"""
    try:
        user = db.query(User).filter(User.id == test.user_id).first()
        if not user:
            logger.error(f"User not found for test {test.id}")
            return
            
        access_token = user.get_google_access_token()
        if not access_token:
            logger.error(f"No access token for user {user.id}, skipping rotation")
            return
        
        current_rotation = db.query(TitleRotation).filter(
            TitleRotation.ab_test_id == test.id,
            TitleRotation.ended_at.is_(None)
        ).first()
        
        youtube_client = YouTubeAPIClient()
        
        if current_rotation:
            try:
                start_date = current_rotation.started_at.strftime('%Y-%m-%d')
                end_date = datetime.utcnow().strftime('%Y-%m-%d')
                
                video_analytics = asyncio.run(youtube_client.get_video_analytics(
                    test.video_id, start_date, end_date, access_token
                ))
                
                current_rotation.views_end = video_analytics.get('views', 0)
                current_rotation.likes_end = video_analytics.get('likes', 0)
                current_rotation.comments_end = video_analytics.get('comments', 0)
                
                if current_rotation.views_start is not None:
                    current_rotation.views_gained = max(0, current_rotation.views_end - current_rotation.views_start)
                
                if current_rotation.views_end > 0 and current_rotation.likes_end is not None:
                    current_rotation.engagement_rate = (current_rotation.likes_end / current_rotation.views_end) * 100
                
                current_rotation.ended_at = datetime.utcnow()
                
                update_quota_usage.delay(user.id, "video_analytics", 1)
                
            except Exception as e:
                logger.error(f"Error fetching end metrics for rotation {current_rotation.id}: {str(e)}")
                current_rotation.ended_at = datetime.utcnow()
            
        next_variant_index = (test.current_variant_index + 1) % len(test.title_variants)
        new_title = test.title_variants[next_variant_index]
        
        try:
            success = asyncio.run(youtube_client.update_video_title(
                test.video_id, new_title, access_token
            ))
            
            if not success:
                logger.error(f"Failed to update video title for test {test.id}")
                return
                
            update_quota_usage.delay(user.id, "videos_update", 50)
            
        except Exception as e:
            logger.error(f"Error updating video title for test {test.id}: {str(e)}")
            return
        
        test.current_variant_index = next_variant_index
        
        try:
            current_date = datetime.utcnow().strftime('%Y-%m-%d')
            
            video_analytics = asyncio.run(youtube_client.get_video_analytics(
                test.video_id, current_date, current_date, access_token
            ))
            
            new_rotation = TitleRotation(
                ab_test_id=test.id,
                variant_index=next_variant_index,
                title=new_title,
                started_at=datetime.utcnow(),
                views_start=video_analytics.get('views', 0),
                likes_start=video_analytics.get('likes', 0),
                comments_start=video_analytics.get('comments', 0)
            )
            
            update_quota_usage.delay(user.id, "video_analytics", 1)
            
        except Exception as e:
            logger.error(f"Error fetching start metrics for new rotation: {str(e)}")
            new_rotation = TitleRotation(
                ab_test_id=test.id,
                variant_index=next_variant_index,
                title=new_title,
                started_at=datetime.utcnow()
            )
        
        db.add(new_rotation)
        
        logger.info(f"Rotated title for test {test.id} to variant {next_variant_index}: '{new_title}'")
        
    except Exception as e:
        logger.error(f"Error performing title rotation for test {test.id}: {str(e)}")
        raise


@current_app.task
def cleanup_completed_tests():
    """Clean up completed tests and update final results"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        tests_to_complete = db.query(ABTest).filter(
            ABTest.status == "active",
            ABTest.started_at.isnot(None)
        ).all()
        
        completed_count = 0
        for test in tests_to_complete:
            time_running = now - test.started_at
            if time_running.total_seconds() >= (test.test_duration_hours * 3600):
                test.status = "completed"
                test.completed_at = now
                
                current_rotation = db.query(TitleRotation).filter(
                    TitleRotation.ab_test_id == test.id,
                    TitleRotation.ended_at.is_(None)
                ).first()
                
                if current_rotation:
                    current_rotation.ended_at = now
                
                completed_count += 1
                
        db.commit()
        logger.info(f"Completed {completed_count} tests")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in cleanup_completed_tests task: {str(e)}")
        raise
    finally:
        db.close()


@current_app.task
def update_quota_usage(user_id: str, api_call_type: str, quota_units: int):
    """Update API quota usage for a user"""
    db = SessionLocal()
    try:
        today = datetime.utcnow().date()
        
        quota_record = db.query(QuotaUsage).filter(
            QuotaUsage.user_id == user_id,
            QuotaUsage.date >= today,
            QuotaUsage.date < today + timedelta(days=1)
        ).first()
        
        if not quota_record:
            quota_record = QuotaUsage(
                user_id=user_id,
                date=datetime.utcnow()
            )
            db.add(quota_record)
        
        quota_record.api_calls_count += 1
        quota_record.quota_units_used += quota_units
        
        if api_call_type == "videos_list":
            quota_record.videos_list_calls += 1
        elif api_call_type == "videos_update":
            quota_record.videos_update_calls += 1
            
        db.commit()
        logger.info(f"Updated quota usage for user {user_id}: +{quota_units} units")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating quota usage: {str(e)}")
        raise
    finally:
        db.close()
