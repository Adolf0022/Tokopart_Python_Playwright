import os
import pytest
import smtplib
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from playwright.sync_api import Page
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.pagesizes import A3
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler()
    ]
)

SMTP_CONFIG = {
    'smtp_server': 'sandbox.smtp.mailtrap.io',
    'smtp_port': 2525,
    'smtp_username': 'd529ebc1ed85b1',
    'smtp_password': '53fbc05d99660d',
    'sender_email': 'adolf.naibaho@mplus.software',
    'recipient_email': 'adolfnaibaho007@gmail.com',
    'timeout': 30
}

@pytest.fixture(scope="session", autouse=True)
def setup_directories():
    Path("reports/screenshots").mkdir(parents=True, exist_ok=True)
    Path("reports/pdf").mkdir(parents=True, exist_ok=True)
    Path("reports/errors").mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"], slow_mo=1000)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page(no_viewport=True)
    page.set_default_timeout(30000)
    yield page
    if not page.is_closed():
        page.close()

@pytest.fixture
def test_context(request):
    if not hasattr(request.session, 'manual_screenshots'):
        request.session.manual_screenshots = []

    def get_or_create_result():
        name = request.node.name
        existing = next((item for item in request.session.manual_screenshots if item["name"] == name), None)
        if existing:
            return existing
        result = {
            "nodeid": request.node.nodeid,
            "name": name,
            "screenshots": [],
            "status": "UNKNOWN"
        }
        request.session.manual_screenshots.append(result)
        return result

    def record(path):
        result = get_or_create_result()
        result["screenshots"].append(path)

    # Save reference to test case data on node
    request.node._manual_test_context = get_or_create_result()

    return {
        "record_screenshot": record
    }

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if call.when == "call" and hasattr(item, "_manual_test_context"):
        item._manual_test_context["status"] = report.outcome.upper()

def generate_pdf_from_manual_screenshots(test_results: List[Dict[str, str]]) -> str:
    try:
        pdf_dir = Path("reports/pdf")
        pdf_path = str(pdf_dir / f"Laporan_Regresi_Tokopart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

        doc = SimpleDocTemplate(pdf_path, pagesize=A3)
        styles = getSampleStyleSheet()

        # Tambahkan style warna status
        styles.add(ParagraphStyle(name='StatusPASSED', parent=styles['Heading3'], textColor=colors.green))
        styles.add(ParagraphStyle(name='StatusFAILED', parent=styles['Heading3'], textColor=colors.red))

        story = []

        story.append(Paragraph("LAPORAN REGRESI TOKOPART", styles['Title']))
        story.append(Spacer(1, 0.2 * inch))

        total = len(test_results)
        passed = sum(1 for t in test_results if t.get("status") == "PASSED")
        failed = total - passed
        tanggal = datetime.now().strftime('%d %B %Y %H:%M')

        story.append(Paragraph(f"Total Scenario: {total} | Passed: {passed} | Failed: {failed}", styles['Heading3']))
        story.append(Paragraph(f"Date: {tanggal}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        for idx, result in enumerate(test_results, start=1):
            if idx > 1:
                story.append(PageBreak())

            name = result["name"]
            status = result.get("status", "UNKNOWN")
            paths = result.get("screenshots", [])

            story.append(Paragraph(f"Testcase #{idx}: {name}", styles['Heading2']))
            style_name = 'StatusPASSED' if status == 'PASSED' else 'StatusFAILED'
            story.append(Paragraph(f"Status: {status}", styles[style_name]))
            story.append(Spacer(1, 0.3 * inch))

            for path in paths:
                if os.path.exists(path):
                    try:
                        img = Image(path, width=6.5 * inch, height=(1000 / 1521) * 6.5 * inch)
                        story.append(img)
                        story.append(Spacer(1, 0.3 * inch))
                    except Exception as e:
                        story.append(Paragraph(f"Gagal memuat gambar: {str(e)}", styles['Italic']))
                else:
                    story.append(Paragraph(f"❌ Screenshot tidak ditemukan: {path}", styles['Italic']))

        doc.build(story)
        logging.info(f"PDF report generated: {pdf_path}")
        return pdf_path

    except Exception as e:
        logging.error(f"PDF generation failed: {str(e)}")
        traceback.print_exc()
        return None

def send_email_with_report(report_path: str) -> bool:
    for attempt in range(3):
        try:
            if not report_path or not os.path.exists(report_path):
                raise FileNotFoundError(f"Report file missing: {report_path}")

            msg = MIMEMultipart()
            msg['From'] = SMTP_CONFIG['sender_email']
            msg['To'] = SMTP_CONFIG['recipient_email']
            msg['Subject'] = f"Laporan Regresi Tokopart - {datetime.now().strftime('%d %B %Y')}"

            email_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Laporan Automation Testing</h2>
                    <p>Berikut hasil regresi terbaru:</p>
                    <p><strong>Waktu Generate:</strong> {datetime.now().strftime('%d %B %Y %H:%M')}</p>
                    <p><strong>File:</strong> Terlampir (PDF Report)</p>
                    <p>Email ini dikirim otomatis oleh sistem automation testing Tokopart.</p>
                </body>
            </html>
            """

            with open(report_path, "rb") as f:
                part = MIMEApplication(f.read(), Name="Laporan_Regresi_Tokopart.pdf")
                part['Content-Disposition'] = 'attachment; filename="Laporan_Regresi_Tokopart.pdf"'
                msg.attach(part)

            msg.attach(MIMEText(email_body, 'html'))

            with smtplib.SMTP(SMTP_CONFIG['smtp_server'], SMTP_CONFIG['smtp_port'], timeout=SMTP_CONFIG['timeout']) as server:
                server.starttls()
                server.login(SMTP_CONFIG['smtp_username'], SMTP_CONFIG['smtp_password'])
                server.send_message(msg)

            logging.info(f"Email berhasil dikirim ke {SMTP_CONFIG['recipient_email']}")
            return True

        except Exception as e:
            logging.warning(f"Percobaan pengiriman email gagal: {str(e)}")
            if attempt < 2:
                import time
                time.sleep(5)

    logging.error("Semua percobaan pengiriman email gagal")
    return False

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    try:
        test_results = getattr(session, 'manual_screenshots', [])
        if test_results:
            logging.info(f"Memproses {len(test_results)} screenshot manual...")

            pdf_path = generate_pdf_from_manual_screenshots(test_results)
            if pdf_path:
                send_email_with_report(pdf_path)
            else:
                logging.error("Gagal membuat laporan PDF")
        else:
            logging.warning("Tidak ada screenshot manual ditemukan.")
    except Exception as e:
        logging.error(f"Error akhir sesi pytest: {str(e)}")
