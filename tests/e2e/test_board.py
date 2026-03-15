"""E2E tests for board editor and preview flows."""
from playwright.sync_api import expect


class TestBoardEditor:
    def test_grid_renders_132_cells(self, page, live_server):
        page.goto(live_server.url)
        cells = page.locator("#board .cell")
        assert cells.count() == 132  # 6 rows * 22 cols

    def test_click_cell_paints(self, page, live_server):
        page.goto(live_server.url)
        # Select letter "A" from picker — open picker first
        page.click("#btn-toggle-picker")
        page.locator(".pick-btn", has_text="A").click()
        # Click first cell
        cell = page.locator("#board .cell").first
        cell.click()
        expect(cell).to_have_attribute("data-code", "1")

    def test_no_js_errors_on_interaction(self, page, live_server, console_errors):
        page.goto(live_server.url)
        page.click("#btn-toggle-picker")
        page.locator(".pick-btn", has_text="A").click()
        page.locator("#board .cell").first.click()
        page.click("#btn-clear")
        assert console_errors == [], f"JS errors: {console_errors}"


class TestBoardPreview:
    def test_preview_renders_on_load(self, page, live_server):
        page.goto(live_server.url)
        preview_cells = page.locator(".sim-cell")
        assert preview_cells.count() == 132

    def test_preview_syncs_with_editor(self, page, live_server):
        page.goto(live_server.url)
        page.click("#btn-toggle-picker")
        page.locator(".pick-btn", has_text="A").click()
        page.locator("#board .cell").first.click()
        # Preview should now have at least one character cell
        preview_chars = page.locator(".sim-cell.ch")
        assert preview_chars.count() > 0

    def test_clear_resets_preview(self, page, live_server):
        page.goto(live_server.url)
        page.click("#btn-toggle-picker")
        page.locator(".pick-btn", has_text="A").click()
        page.locator("#board .cell").first.click()
        page.click("#btn-clear")
        preview_chars = page.locator(".sim-cell.ch")
        assert preview_chars.count() == 0


class TestTextMode:
    def test_text_input_updates_board(self, page, live_server):
        page.goto(live_server.url)
        page.fill("#text-input", "HELLO")
        # Board should now have non-blank cells
        non_blank = page.locator('.cell:not([data-code="0"])')
        assert non_blank.count() > 0

    def test_no_js_errors_text_mode(self, page, live_server, console_errors):
        page.goto(live_server.url)
        page.fill("#text-input", "TEST")
        assert console_errors == [], f"JS errors: {console_errors}"
