import pytest
from unittest.mock import patch, MagicMock
from automations.base import BaseAutomation
import automations.scheduler as scheduler


class DummyAutomation(BaseAutomation):
    name = "dummy"
    schedule = "30 9 * * *"

    async def run(self):
        return [[0] * 22 for _ in range(6)]


class TestScheduler:
    def setup_method(self):
        """Reset scheduler state before each test."""
        scheduler._automations.clear()
        # Remove any existing jobs
        for job in scheduler._scheduler.get_jobs():
            job.remove()

    def test_register_stores_automation(self):
        auto = DummyAutomation()
        scheduler.register(auto)
        assert "dummy" in scheduler.get_automations()
        assert scheduler.get_automations()["dummy"] is auto

    def test_register_creates_job(self):
        auto = DummyAutomation()
        scheduler.register(auto)
        job_ids = [j.id for j in scheduler._scheduler.get_jobs()]
        assert "dummy" in job_ids

    def test_get_jobs_returns_schedule(self):
        auto = DummyAutomation()
        scheduler.register(auto)
        scheduler.start()
        try:
            jobs = scheduler.get_jobs()
            assert len(jobs) >= 1
            job = next(j for j in jobs if j["name"] == "dummy")
            assert job["schedule"] == "30 9 * * *"
            assert job["next_run"] is not None
        finally:
            scheduler.stop()

    def test_register_replaces_existing(self):
        auto1 = DummyAutomation()
        auto2 = DummyAutomation()
        scheduler.start()
        try:
            scheduler.register(auto1)
            scheduler.register(auto2)
            # Should still have one job, not two
            job_ids = [j.id for j in scheduler._scheduler.get_jobs()]
            assert job_ids.count("dummy") == 1
            assert scheduler.get_automations()["dummy"] is auto2
        finally:
            scheduler.stop()
