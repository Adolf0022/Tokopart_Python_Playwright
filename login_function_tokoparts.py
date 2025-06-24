from playwright.sync_api import Playwright, Page, expect, sync_playwright
import time
from datetime import datetime

def login_scm(page: Page):        
    page.goto("https://scm.tokoparts.mitija-dev.net/")
    page.locator(f"#username").fill("Admin")
    time.sleep(2)
    page.locator(f"#password").fill("bukan_raHasi4")
    time.sleep(2)
    page.locator('[class="btn btn-primary-red btn-block"]').click()
    time.sleep(2)
    expect(page.locator("h1")).to_have_text("Welcome")
    time.sleep(2)
    page.locator("h1").text_content()
    time.sleep(2)
