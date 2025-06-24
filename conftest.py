import os
import pytest
import re
import traceback
import smtplib
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from playwright.sync_api import Page
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from reportlab.platypus import PageBreak 
from reportlab.lib.units import inch 


TestResult = Dict[str, str]

# Konfigurasi SMTP Mailtrap
SMTP_CONFIG = {
    'smtp_server': 'sandbox.smtp.mailtrap.io',
    'smtp_port': 2525,
    'smtp_username': '3fbe4b55b5c28f',
    'smtp_password': 'c4f4efe22fe0fe',
    'sender_email': 'adolf.naibaho@mplus.software',
    'recipient_email': 'adolfnaibaho007@gmail.com',
    'timeout': 10
}

@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if not hasattr(item.session, 'all_test_results'):
        item.session.all_test_results = []
    
    if report.when == "call":
        page = item.funcargs.get("page")
        test_data = {
            "nodeid": item.nodeid,
            "name": item.name,
            "status": report.outcome.upper(),
            "duration": report.duration,
            "timestamp": datetime.now().isoformat(),
            "error": str(report.longrepr) if report.failed else None,
            "screenshot_path": None
        }
        
        if page:
            screenshot_dir = Path("reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            test_name = re.sub(r'[\\/*?:"<>|]', "_", item.nodeid.split("::")[-1]) + ".png"
            screenshot_path = str(screenshot_dir / test_name)
            
            original_viewport = page.viewport_size
            try:
                # [FIXED] Pertahankan pengaturan viewport dan clip area
                page.set_viewport_size({"width": 1536, "height": 1000})
                page.wait_for_timeout(2000)  # Tunggu render setelah resize
                
                # [FIXED] Gunakan clip area yang spesifik
                page.screenshot(
                    path=screenshot_path,
                    clip={"x": 0, "y": 0, "width": 1536, "height": 1000},
                    timeout=10000
                )
                
                if os.path.exists(screenshot_path):
                    test_data["screenshot_path"] = screenshot_path
                    print(f"✅ Screenshot saved: {screenshot_path}")
                else:
                    print(f"⚠️ Screenshot file not created: {screenshot_path}")
                    
            except Exception as e:
                print(f"⚠️ Gagal mengambil screenshot: {e}")
                traceback.print_exc()
            finally:
                # Kembalikan viewport ke ukuran semula
                if original_viewport:
                    page.set_viewport_size(original_viewport)
        
        item.session.all_test_results.append(test_data)

def generate_pdf_report(test_results: List[TestResult]) -> str:
    try:
        pdf_dir = Path("reports/pdf")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = str(pdf_dir / f"Test_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                              leftMargin=0.75*inch,
                              rightMargin=0.75*inch,
                              topMargin=0.5*inch,
                              bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Header Cover
        story.append(Paragraph("Laporan Automation Testing Tokopart", 
                             styles['Title']))
        story.append(Spacer(1, 0.25*inch))
        
        # Summary Info
        passed = sum(1 for t in test_results if t['status'] == 'PASSED')
        failed = len(test_results) - passed
        story.append(Paragraph(
            f"<b>Total Test:</b> {len(test_results)} | "
            f"<b>Passed:</b> {passed} | "
            f"<b>Failed:</b> {failed} | "
            f"<b>Tanggal:</b> {datetime.now().strftime('%d %B %Y')}",
            styles['Heading3']
        ))
        story.append(Spacer(1, 6))
        
        # Test Case #1
        if len(test_results) > 0:
            first_test = test_results[0]
            status_color = colors.green if first_test['status'] == 'PASSED' else colors.red
            
            # Test Case Header
            story.append(Paragraph(
                f"Test Case #1: {first_test['name']}",
                styles['Heading1']
            ))
            story.append(Spacer(1, 0.6))
            
            # Status
            story.append(Paragraph(
                f"<font color='{status_color}'>Status: {first_test['status']}</font> | "
                f"Durasi: {first_test['duration']:.2f}s",
                styles['Heading3']
            ))
            story.append(Spacer(1, 0.6))
            
            # Screenshot
            if first_test['screenshot_path']:
                try:
                    img = Image(first_test['screenshot_path'],
                              width=5.5*inch,  # Sedikit lebih kecil
                              height=3.58*inch)  # Maintain aspect ratio
                    story.append(img)
                    story.append(Spacer(1, 6))
                except Exception as e:
                    story.append(Paragraph(
                        "⚠️ Gagal memuat screenshot: " + str(e),
                        styles['Italic']
                    ))
            
            # Error Message
            if first_test['error']:
                story.append(Paragraph("Detail Error:", styles['Heading4']))
                story.append(Paragraph(first_test['error'], styles['Code']))
        
        # Halaman baru untuk test case berikutnya
        if len(test_results) > 1:
            story.append(PageBreak())

        for idx, test in enumerate(test_results[1:], start=2):
            status_color = colors.green if test['status'] == 'PASSED' else colors.red
            
            # Header
            story.append(Paragraph(
                f"Test Case #{idx}: {test['name']}",
                styles['Heading1']
            ))
            story.append(Spacer(1, 6))
            
            # Status
            story.append(Paragraph(
                f"<font color='{status_color}'>Status: {test['status']}</font> | "
                f"Durasi: {test['duration']:.2f}s",
                styles['Heading3']
            ))
            story.append(Spacer(1, 6))
            
            # Screenshot (ukuran penuh)
            if test['screenshot_path']:
                try:
                    img = Image(test['screenshot_path'],
                              width=6*inch,
                              height=3.9*inch)
                    story.append(img)
                    story.append(Spacer(1, 0.1*inch))
                except Exception as e:
                    story.append(Paragraph(
                        "⚠️ Gagal memuat screenshot: " + str(e),
                        styles['Italic']
                    ))
            
            # Error Message
            if test['error']:
                story.append(Paragraph("Detail Error:", styles['Heading4']))
                story.append(Paragraph(test['error'], styles['Code']))
            
            # Page break kecuali untuk test case terakhir
            if idx < len(test_results):
                story.append(PageBreak())
        
        doc.build(story)
        print(f"✅ PDF report generated: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ Gagal generate PDF: {str(e)}")
        traceback.print_exc()
        return None

def send_email_with_report(pdf_path: str) -> bool:
    """Mengirim laporan PDF via SMTP"""
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File PDF tidak ditemukan: {pdf_path}")

        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['sender_email']
        msg['To'] = SMTP_CONFIG['recipient_email']
        msg['Subject'] = f"Laporan Testing Tokopart - {datetime.now().strftime('%d/%m/%Y')}"
        
        body = f"""
        <html>
            <body style="font-family:Arial,sans-serif;">
                <h2 style="color:#2a5885;border-bottom:1px solid #eee;padding-bottom:8px;">
                    Laporan Automation Testing Tokopart
                </h2>
                <p>Berikut Hasil Regresi Terbaru:</p>
                <ul style="line-height:1.6;padding-left:20px;">
                    <li><strong>Waktu Generate:</strong> {datetime.now().strftime('%d %B %Y %H:%M')}</li>
                    <li><strong>Scenario:</strong> 
                        <a href="https://docs.google.com/spreadsheets/d/1PaPr6YelsyxuTYe9GVNgv2ztAGLu3WvKS6g8rOXMyHI/edit?gid=1771717336" 
                        style="color:#1a73e8;text-decoration:underline;">
                        Link Test Scenario (Google Sheets)
                        </a>
                    </li>
                    <li><strong>File:</strong> Laporan PDF terlampir</li>
                </ul>
                <p style="margin-top:20px;color:#666;font-size:0.9em;">
                    Email otomatis | Tokopart QA Automation
                </p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        with open(pdf_path, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', 
                            filename=f"Laporan_Test_{datetime.now().strftime('%Y%m%d')}.pdf")
            msg.attach(attach)
        
        with smtplib.SMTP(
            host=SMTP_CONFIG['smtp_server'],
            port=SMTP_CONFIG['smtp_port'],
            timeout=SMTP_CONFIG['timeout']
        ) as server:
            server.set_debuglevel(1)  # Debug output
            server.starttls()
            server.login(SMTP_CONFIG['smtp_username'], SMTP_CONFIG['smtp_password'])
            server.send_message(msg)
        
        print(f"✅ Email berhasil dikirim ke {SMTP_CONFIG['recipient_email']}")
        return True
        
    except Exception as e:
        print(f"❌ Gagal mengirim email: {str(e)}")
        traceback.print_exc()
        return False

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    if hasattr(session, 'all_test_results'):
        print(f"\n{'='*50}\nMemproses {len(session.all_test_results)} test results...")
        
        pdf_path = generate_pdf_report(session.all_test_results)
        
        if pdf_path and os.path.exists(pdf_path):
            print(f"Mengirim email dengan laporan: {pdf_path}")
            send_email_with_report(pdf_path)
        else:
            print("❌ Tidak ada PDF yang dikirim")