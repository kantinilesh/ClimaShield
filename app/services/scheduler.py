"""
ClimaShield – Scheduler Service
APScheduler-based job scheduling for background tasks.

Jobs:
  - Oracle monitoring: every 5 minutes
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger("climashield.scheduler")

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def _run_oracle_check():
    """Wrapper to run oracle worker in scheduler context."""
    from workers.oracle_worker import check_weather_triggers
    try:
        result = await check_weather_triggers()
        logger.info(f"[SCHEDULER] Oracle check complete: {result.get('triggers_detected', 0)} triggers")
    except Exception as e:
        logger.error(f"[SCHEDULER] Oracle check failed: {e}")


def start_scheduler():
    """
    Start the background scheduler with all jobs.
    Call this during FastAPI startup.
    """
    # Oracle monitoring every 5 minutes
    scheduler.add_job(
        _run_oracle_check,
        IntervalTrigger(minutes=5),
        id="oracle_monitoring",
        name="Oracle Weather Monitoring",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("[SCHEDULER] Background scheduler started (oracle monitoring every 5 min)")


def stop_scheduler():
    """Stop the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[SCHEDULER] Scheduler stopped")


def get_scheduler_status() -> dict:
    """Get status of all scheduled jobs."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    return {
        "running": scheduler.running,
        "jobs": jobs,
    }
