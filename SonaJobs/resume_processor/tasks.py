from celery import shared_task
from django.utils import timezone
import logging
from .processor import ResumeProcessor
from accounts.models import User, JobSeekerProfile
from jobs.models import JobRecommendation

logger = logging.getLogger(__name__)

@shared_task
def run_auto_talent_match(user_id: int):
    """
    Background task to automatically match a user's profile against active jobs.
    Rate limited to 3 matches per day per user.
    """
    try:
        user = User.objects.get(id=user_id)
        if not hasattr(user, 'jobseeker_profile'):
            logger.warning(f"User {user_id} does not have a jobseeker profile")
            return "No jobseeker profile"
            
        profile = user.jobseeker_profile
        
        # Check if enabled
        if not profile.auto_match_enabled:
            logger.info(f"Auto-match disabled for user {user_id}")
            return "Auto-match disabled"
            
        # Check rate limits
        now = timezone.now()
        if profile.last_auto_match and profile.last_auto_match.date() != now.date():
            # Reset daily count
            profile.auto_match_count_today = 0
            
        if profile.auto_match_count_today >= 3:
            logger.info(f"Rate limit exceeded for user {user_id} today")
            return "Rate limit exceeded (max 3/day)"
            
        # Run match
        processor = ResumeProcessor()
        matches = processor.match_profile_to_available_jobs(profile)
        
        # Save recommendations
        new_recommendations = 0
        for match in matches:
            from jobs.models import Job
            try:
                job = Job.objects.get(id=match['job_id'])
                # Update or create recommendation
                recommendation, created = JobRecommendation.objects.update_or_create(
                    job_seeker=profile,
                    job=job,
                    defaults={'score': match['match_score']}
                )
                if created:
                    new_recommendations += 1
            except Job.DoesNotExist:
                pass
                
        # Update rate limit tracking
        profile.last_auto_match = now
        profile.auto_match_count_today += 1
        profile.save()
        
        logger.info(f"Auto-match completed for {user_id}. Found {new_recommendations} new matches out of {len(matches)} total.")
        return f"Found {new_recommendations} new matches"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for auto match")
        return "User not found"
    except Exception as e:
        logger.error(f"Error in auto_talent_match for {user_id}: {e}")
        return str(e)
