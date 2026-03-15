"""E2E tests for automation flows in the web UI."""
import pytest
from playwright.sync_api import expect


class TestAutomationList:
    def test_weather_automation_visible(self, page, live_server):
        page.goto(live_server.url)
        automation_list = page.locator("#automation-list")
        expect(automation_list).to_contain_text("weather")

    def test_run_button_exists(self, page, live_server):
        page.goto(live_server.url)
        run_btn = page.locator("#automation-list button", has_text="Run")
        expect(run_btn).to_be_visible()


class TestTriggerAutomation:
    def test_no_js_errors_on_page_load(self, page, live_server, console_errors):
        page.goto(live_server.url)
        page.wait_for_timeout(500)
        assert console_errors == [], f"JS errors on load: {console_errors}"

    def test_no_js_errors_on_trigger(self, page, live_server, console_errors):
        page.goto(live_server.url)
        run_btn = page.locator("#automation-list button", has_text="Run")
        run_btn.click()
        page.wait_for_timeout(3000)  # wait for API call to complete
        assert console_errors == [], f"JS errors on trigger: {console_errors}"

    def test_trigger_shows_running_toast(self, page, live_server):
        page.goto(live_server.url)
        run_btn = page.locator("#automation-list button", has_text="Run")
        run_btn.click()
        toast = page.locator(".toast").first
        expect(toast).to_be_visible(timeout=2000)
        expect(toast).to_contain_text("Running")

    def test_trigger_shows_success_toast(self, page, live_server):
        page.goto(live_server.url)
        run_btn = page.locator("#automation-list button", has_text="Run")
        run_btn.click()
        # Wait for the success toast (second one after "Running...")
        success_toast = page.locator(".toast.ok")
        expect(success_toast).to_be_visible(timeout=10000)
        expect(success_toast).to_contain_text("sent!")

    def test_trigger_updates_editor_grid(self, page, live_server):
        page.goto(live_server.url)
        run_btn = page.locator("#automation-list button", has_text="Run")
        run_btn.click()
        # Wait for success
        success_toast = page.locator(".toast.ok")
        expect(success_toast).to_be_visible(timeout=10000)
        # Board should have non-blank cells (weather data)
        non_blank = page.locator('.cell:not([data-code="0"])')
        assert non_blank.count() > 0, "Board should have non-blank cells after trigger"

    def test_trigger_updates_preview(self, page, live_server):
        page.goto(live_server.url)
        run_btn = page.locator("#automation-list button", has_text="Run")
        run_btn.click()
        success_toast = page.locator(".toast.ok")
        expect(success_toast).to_be_visible(timeout=10000)
        # Preview should have character cells
        preview_chars = page.locator(".sim-cell.ch")
        assert preview_chars.count() > 0, "Preview should have character cells after trigger"
