from playwright.sync_api import Page, expect, sync_playwright
import time
from based_Function import *

def test_case_1_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Reguler(page)
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()
    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Reguler(page)
        Search_Lala_Reguler(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)
    else:
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)

def test_case_2_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Sameday(page)
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()
    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Sameday(page)
        Search_Lala_Sameday(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)
    else:
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)

def test_case_3_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Instant(page)
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()
    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Instant(page)
        Search_Lala_Instant(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)
    else:
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)

def test_case_4_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Other_Reguler(page)
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()
    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Other_Reguler(page)
        Search_Other_Reguler(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)
    else:
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)

def test_case_5_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Other_SameDay(page)
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()
    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Other_SameDay(page)
        Search_Other_SameDay(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)
    else:
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)  

def test_case_6_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Other_Instant(page)
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()
    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Other_Instant(page)
        Search_Other_Instant(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)
    else:
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)  

def test_case_7_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Reguler(page)
    page.locator('#btn_adv_search').click()
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()

    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Reguler(page)
        Search_Lala_Reguler(page)
        screenshoot(page, test_context)
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        page.press('body', "Enter")
        screenshoot(page, test_context)
        Create_Lala_Instant(page)
        Search_Lala_Instant(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
    else:
    # Click the 'Edit' button if text doesn't match
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        screenshoot(page, test_context)
        Create_Lala_Instant(page)
        Search_Lala_Instant(page)
        screenshoot(page, test_context)
        time.sleep(1)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)

def test_case_8_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Reguler(page)
    page.locator('#btn_adv_search').click()
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()

    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Reguler(page)
        Search_Lala_Reguler(page)
        screenshoot(page, test_context)
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        page.press('body', "Enter")
        screenshoot(page, test_context)
        Create_Lala_Sameday(page)
        Search_Lala_Sameday(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
    else:
    # Click the 'Edit' button if text doesn't match
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        screenshoot(page, test_context)
        Create_Lala_Sameday(page)
        Search_Lala_Sameday(page)
        screenshoot(page, test_context)
        time.sleep(1)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)

def test_case_9_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Instant(page)
    page.locator('#btn_adv_search').click()
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()

    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Instant(page)
        Search_Lala_Instant(page)
        screenshoot(page, test_context)
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        page.press('body', "Enter")
        screenshoot(page, test_context)
        Create_Lala_Sameday(page)
        Search_Lala_Sameday(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
    else:
    # Click the 'Edit' button if text doesn't match
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        screenshoot(page, test_context)
        Create_Lala_Sameday(page)
        Search_Lala_Sameday(page)
        screenshoot(page, test_context)
        time.sleep(1)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)

def test_case_10_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Instant(page)
    page.locator('#btn_adv_search').click()
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()

    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Instant(page)
        Search_Lala_Instant(page)
        screenshoot(page, test_context)
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        page.press('body', "Enter")
        screenshoot(page, test_context)
        Create_Lala_Reguler(page)
        Search_Lala_Reguler(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
    else:
    # Click the 'Edit' button if text doesn't match
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        screenshoot(page, test_context)
        Create_Lala_Reguler(page)
        Search_Lala_Reguler(page)
        screenshoot(page, test_context)
        time.sleep(1)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)

def test_case_11_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Sameday(page)
    page.locator('#btn_adv_search').click()
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()

    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Sameday(page)
        Search_Lala_Sameday(page)
        screenshoot(page, test_context)
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        page.press('body', "Enter")
        screenshoot(page, test_context)
        Create_Lala_Reguler(page)
        Search_Lala_Reguler(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
    else:
    # Click the 'Edit' button if text doesn't match
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        screenshoot(page, test_context)
        Create_Lala_Reguler(page)
        Search_Lala_Reguler(page)
        screenshoot(page, test_context)
        time.sleep(1)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)

def test_case_12_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Sameday(page)
    page.locator('#btn_adv_search').click()
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()

    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Sameday(page)
        Search_Lala_Sameday(page)
        screenshoot(page, test_context)
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        page.press('body', "Enter")
        screenshoot(page, test_context)
        Create_Lala_Instant(page)
        Search_Lala_Instant(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
    else:
    # Click the 'Edit' button if text doesn't match
        page.locator('[class="btn btn-sm btn-default btn-black pull-right ml-1 btn-edit"]').click()
        page.locator("#status").select_option(value="INACTIVE") 
        time.sleep(1)
        page.get_by_role("button", name="Save").click()
        time.sleep(1)
        expect(page.locator('.swal-title')).to_have_text("Berhasil!")
        expect(page.locator('.swal-text')).to_have_text("Data berhasil disimpan")
        time.sleep(1)
        screenshoot(page, test_context)
        Create_Lala_Instant(page)
        Search_Lala_Instant(page)
        screenshoot(page, test_context)
        time.sleep(1)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context) 

def test_case_13_UserStory2(page: Page, test_context):
    login_frontline(page)
    Add_Product_To_Cart(page)
    screenshoot(page, test_context)


def test_case_14_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Reguler(page)
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()
    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Reguler(page)
        Search_Lala_Reguler(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)
    else:
        login_frontline(page)
        Add_Product_To_Cart_With_COD(page)
        screenshoot(page, test_context)
        time.sleep(1)

def test_case_15_UserStory2(page: Page, test_context):
    login_scm(page)
    Search_Lala_Reguler(page)
    time.sleep(1)
    text = page.locator("td").nth(0).inner_text()
    # Check if the text is "No data available in table"
    if text == "No data available in table":
        Create_Lala_Reguler(page)
        Search_Lala_Reguler(page)
        screenshoot(page, test_context)
        login_frontline(page)
        Add_Product_To_Cart(page)
        screenshoot(page, test_context)
        time.sleep(1)
    else:
        login_frontline(page)
        Add_Product_To_Cart_With_COD(page)
        screenshoot(page, test_context)
        time.sleep(1)


if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page() 
