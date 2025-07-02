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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

TestResult = Dict[str, str]

# Konfigurasi SMTP (Mailtrap)
SMTP_CONFIG = {
    'smtp_server': 'sandbox.smtp.mailtrap.io',
    'smtp_port': 2525,
    'smtp_username': 'your_mailtrap_username',
    'smtp_password': 'your_mailtrap_password',
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
    
    if report.when in ["call", "setup"]:  # Tangkap setup dan call
        test_data = {
            "nodeid": item.nodeid,
            "name": item.name,
            "status": report.outcome.upper(),
            "duration": getattr(report, "duration", 0),
            "timestamp": datetime.now().isoformat(),
            "error": str(report.longrepr) if report.failed else None,
            "screenshot_path": None
        }
        
        page = item.funcargs.get("page")
        if page:
            try:
                screenshot_dir = Path("reports/screenshots")
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                
                test_name = re.sub(r'[\\/*?:"<>|]', "_", item.nodeid.split("::")[-1]) + ".png"
                screenshot_path = str(screenshot_dir / test_name)
                
                # Ambil screenshot dengan ukuran tetap
                original_viewport = page.viewport_size
                page.set_viewport_size({"width": 1536, "height": 1000})
                page.wait_for_timeout(1000)  # Tunggu render
                
                page.screenshot(
                    path=screenshot_path,
                    clip={"x": 0, "y": 0, "width": 1536, "height": 1000},
                    timeout=30000
                )
                
                if os.path.exists(screenshot_path):
                    test_data["screenshot_path"] = screenshot_path
                
                # Kembalikan viewport asli
                if original_viewport:
                    page.set_viewport_size(original_viewport)
                    
            except Exception as e:
                print(f"⚠️ Gagal ambil screenshot: {str(e)}")
                traceback.print_exc()
        
        item.session.all_test_results.append(test_data)

def generate_pdf_report(test_results: List[TestResult]) -> str:
    """Generate PDF report dengan 1 test case per halaman"""
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
        
        # Halaman Cover
        story.append(Paragraph("Laporan Automation Testing Tokopart", styles['Title']))
        story.append(Spacer(1, 0.25*inch))
        
        passed = sum(1 for t in test_results if t['status'] == 'PASSED')
        failed = len(test_results) - passed
        story.append(Paragraph(
            f"<b>Total Test:</b> {len(test_results)} | "
            f"<b>Passed:</b> {passed} | "
            f"<b>Failed:</b> {failed} | "
            f"<b>Tanggal:</b> {datetime.now().strftime('%d %B %Y')}",
            styles['Heading2']
        ))
        
        # Test Case #1 di halaman yang sama
        if test_results:
            first_test = test_results[0]
            add_test_case_to_story(story, first_test, 1, styles)
        
        # Halaman baru untuk test case berikutnya
        for idx, test in enumerate(test_results[1:], start=2):
            story.append(PageBreak())
            add_test_case_to_story(story, test, idx, styles)
        
        doc.build(story)
        print(f"✅ PDF report generated: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ Gagal generate PDF: {str(e)}")
        traceback.print_exc()
        return None

def add_test_case_to_story(story, test, idx, styles):
    """Helper untuk menambahkan test case ke story"""
    status_color = colors.green if test['status'] == 'PASSED' else colors.red
    
    # Header
    story.append(Paragraph(
        f"Test Case #{idx}: {test['name']}", 
        styles['Heading1']
    ))
    story.append(Spacer(1, 0.1*inch))
    
    # Status
    story.append(Paragraph(
        f"<font color='{status_color}'>Status: {test['status']}</font> | "
        f"Durasi: {test['duration']:.2f}s | "
        f"Waktu: {test['timestamp']}",
        styles['Heading3']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Screenshot
    if test['screenshot_path'] and os.path.exists(test['screenshot_path']):
        try:
            img = Image(test['screenshot_path'], 
                      width=6*inch, 
                      height=3.9*inch)  # 1536x1000 pixels
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
                <h2 style="color:#2a5885;">Laporan Automation Testing</h2>
                <p>Berikut Hasil Regresi Tokopart Terbaru:</p>
                <ul style="line-height:1.6;">
                    <li><strong>Waktu Generate:</strong> {datetime.now().strftime('%d %B %Y %H:%M')}</li>
                    <li><strong>Scenario:</strong> <a href="https://docs.google.com/spreadsheets/d/1PaPr6YelsyxuTYe9GVNgv2ztAGLu3WvKS6g8rOXMyHI/edit?gid=1771717336" 
                       style="color:#1a73e8;text-decoration:underline;">
                       Link Google Sheets Test Scenario</a></li>
                    <li><strong>File:</strong> Terlampir (PDF Report)</li>
                </ul>
                <p style="margin-top:20px;color:#666;">
                    Email ini dikirim otomatis oleh sistem automation testing Tokopart.
                </p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Lampiran PDF
        with open(pdf_path, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', 
                            filename=f"Laporan_Regresi_{datetime.now().strftime('%Y%m%d')}.pdf")
            msg.attach(attach)
        
        # Kirim email dengan debug
        with smtplib.SMTP(
            host=SMTP_CONFIG['smtp_server'],
            port=SMTP_CONFIG['smtp_port'],
            timeout=SMTP_CONFIG['timeout']
        ) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login(SMTP_CONFIG['smtp_username'], SMTP_CONFIG['smtp_password'])
            server.send_message(msg)
        
        print(f"✅ Email terkirim ke {SMTP_CONFIG['recipient_email']}")
        return True
        
    except Exception as e:
        print(f"❌ Gagal mengirim email: {str(e)}")
        traceback.print_exc()
        return False

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    if hasattr(session, 'all_test_results'):
        print(f"\n{'='*50}")
        print(f"Memproses {len(session.all_test_results)} test results...")
        
        try:
            pdf_path = generate_pdf_report(session.all_test_results)
            
            if pdf_path and os.path.exists(pdf_path):
                print(f"📨 Mengirim email dengan laporan: {pdf_path}")
                if send_email_with_report(pdf_path):
                    print("✅ Proses laporan selesai")
                else:
                    print("⚠️ Laporan PDF dibuat tapi email gagal dikirim")
            else:
                print("❌ Gagal generate PDF report")
                
        except Exception as e:
            print(f"❌ Error dalam proses reporting: {str(e)}")
            traceback.print_exc()