import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from automations.base import BaseAutomation
import vesta.client as client

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler()
_automations: dict[str, BaseAutomation] = {}
_last_runs: dict[str, str] = {}


def record_last_run(name: str) -> None:
    """Record the current time as the last run time for an automation."""
    _last_runs[name] = datetime.now(timezone.utc).isoformat()


def _make_job(automation: BaseAutomation):
    """Create a job function for the given automation."""
    def _job():
        loop = asyncio.new_event_loop()
        try:
            board = loop.run_until_complete(automation.run())
            client.send(board)
            record_last_run(automation.name)
            logger.info(f"Automation '{automation.name}' sent board successfully.")
        except Exception as e:
            logger.error(f"Automation '{automation.name}' failed: {e}")
        finally:
            loop.close()
    return _job


def _parse_cron(schedule: str) -> CronTrigger:
    parts = schedule.split()
    return CronTrigger(
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        day_of_week=parts[4],
    )


def register(automation: BaseAutomation) -> None:
    """Register an automation and schedule it via cron."""
    _automations[automation.name] = automation
    _scheduler.add_job(
        _make_job(automation),
        trigger=_parse_cron(automation.schedule),
        id=automation.name,
        replace_existing=True,
    )
    logger.info(f"Registered automation '{automation.name}' with schedule '{automation.schedule}'")


def reschedule(name: str, schedule: str) -> None:
    """Update the cron schedule for a registered automation."""
    if name not in _automations:
        return
    _automations[name].schedule = schedule
    _scheduler.reschedule_job(name, trigger=_parse_cron(schedule))
    logger.info(f"Rescheduled automation '{name}' to '{schedule}'")


def get_automations() -> dict[str, BaseAutomation]:
    return _automations


def get_jobs() -> list[dict]:
    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "name": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "last_run": _last_runs.get(job.id),
            "schedule": _automations[job.id].schedule if job.id in _automations else None,
        })
    return jobs


def start() -> None:
    _scheduler.start()
    logger.info("Scheduler started.")


def stop() -> None:
    _scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")
