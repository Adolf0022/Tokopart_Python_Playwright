import os
import pytest
import re
import traceback
import smtplib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from playwright.sync_api import Page
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from reportlab.lib.units import inch

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

TestResult = Dict[str, str]

# SMTP Configuration
SMTP_CONFIG = {
    'smtp_server': 'sandbox.smtp.mailtrap.io',
    'smtp_port': 2525,
    'smtp_username': 'ad529ebc1ed85b1',
    'smtp_password': 'a53fbc05d99660d',
    'sender_email': 'adolf.naibaho@mplus.software',
    'recipient_email': 'adolfnaibaho007@gmail.com',
    'timeout': 30
}

@pytest.fixture(scope="session", autouse=True)
def setup_directories():
    """Create necessary directories before tests run"""
    Path("reports/screenshots").mkdir(parents=True, exist_ok=True)
    Path("reports/pdf").mkdir(parents=True, exist_ok=True)
    Path("reports/errors").mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"],
            slow_mo=1000
        )
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page(no_viewport=True)
    page.set_default_timeout(30000)
    yield page
    if not page.is_closed():
        page.close()

def sanitize_error_message(error_text: str) -> str:
    """Clean error messages for PDF compatibility"""
    if not error_text:
        return ""
    
    # Replace problematic characters
    error_text = str(error_text)
    replacements = {
        '<': '&lt;',
        '>': '&gt;',
        '\n': '<br/>',
        '"': '&quot;',
        "'": '&apos;'
    }
    for char, replacement in replacements.items():
        error_text = error_text.replace(char, replacement)
    return error_text

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
            "error": sanitize_error_message(report.longrepr) if report.failed else None,
            "screenshot_path": None
        }
        
        if page and not page.is_closed():
            try:
                screenshot_dir = Path("reports/screenshots")
                test_name = re.sub(r'[\\/*?:"<>|\s]', "_", item.nodeid.split("::")[-1])
                screenshot_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{test_name}.png"
                screenshot_path = str(screenshot_dir / screenshot_name)
                
                # Save original viewport
                original_viewport = page.viewport_size
                
                # Set fixed 1536x1000 viewport
                page.set_viewport_size({"width": 1536, "height": 1000})
                page.wait_for_timeout(1000)
                
                # Take precise screenshot
                page.screenshot(
                    path=screenshot_path,
                    clip={"x": 0, "y": 0, "width": 1536, "height": 1000},
                    timeout=10000
                )
                
                if os.path.exists(screenshot_path):
                    test_data["screenshot_path"] = screenshot_path
                    logging.info(f"1536x1000 screenshot saved: {screenshot_path}")
                
            except Exception as e:
                logging.error(f"Screenshot failed: {e}")
            finally:
                # Restore original viewport
                if original_viewport:
                    page.set_viewport_size(original_viewport)
        
        item.session.all_test_results.append(test_data)

def generate_pdf_report(test_results: List[TestResult]) -> str:
    """Generate PDF report that always works, even with failed tests"""
    try:
        pdf_dir = Path("reports/pdf")
        pdf_path = str(pdf_dir / f"Laporan_Regresi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='PassedStyle',
            parent=styles['Heading2'],
            textColor=colors.green,
            spaceAfter=6
        ))
        styles.add(ParagraphStyle(
            name='FailedStyle',
            parent=styles['Heading2'],
            textColor=colors.red,
            spaceAfter=6
        ))
        
        # Cover Page
        story.append(Paragraph("LAPORAN REGRESI TOKOPART", styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        
        # Summary
        passed = sum(1 for t in test_results if t.get('status') == 'PASSED')
        failed = len(test_results) - passed
        summary_text = f"""
        <b>Total Test:</b> {len(test_results)}<br/>
        <b>Berhasil:</b> {passed}<br/>
        <b>Gagal:</b> {failed}<br/>
        <b>Tanggal:</b> {datetime.now().strftime('%d %B %Y %H:%M')}
        """
        story.append(Paragraph(summary_text, styles['Heading3']))
        
        # Test Cases
        for idx, test in enumerate(test_results, start=1):
            if idx > 1:  # Page break for subsequent tests
                story.append(PageBreak())
                
            status_style = 'PassedStyle' if test['status'] == 'PASSED' else 'FailedStyle'
            
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(f"TEST CASE #{idx}: {test['name']}", styles['Heading1']))
            story.append(Paragraph(f"Status: {test['status']}", styles[status_style]))
            story.append(Paragraph(f"Durasi: {test['duration']:.2f}s", styles['Normal']))
            
            # Screenshot
            if test.get('screenshot_path') and os.path.exists(test['screenshot_path']):
                try:
                    img = Image(test['screenshot_path'], 
                              width=6*inch, 
                              height=(1000/1536)*6*inch)
                    story.append(Spacer(1, 0.2*inch))
                    story.append(Paragraph("Evidence:", styles['Heading3']))
                    story.append(img)
                except Exception as e:
                    story.append(Paragraph(f"Gagal memuat screenshot: {str(e)}", styles['Italic']))
            
            # Error details
            if test.get('error'):
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph("DETAIL ERROR:", styles['Heading3']))
                story.append(Paragraph(test['error'], styles['Code']))
        
        doc.build(story)
        logging.info(f"PDF report generated: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logging.error(f"PDF generation failed: {str(e)}")
        traceback.print_exc()
        
        # Create error report
        error_path = str(Path("reports/errors") / f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        try:
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(f"PDF Generation Failed at {datetime.now()}\n")
                f.write(f"Error: {str(e)}\n\n")
                f.write("Test Results Summary:\n")
                for test in test_results:
                    f.write(f"- {test.get('name')}: {test.get('status')}\n")
                    if test.get('error'):
                        f.write(f"  Error: {test.get('error')}\n")
            return error_path
        except Exception as backup_error:
            logging.error(f"Could not create error report: {str(backup_error)}")
            return None

def send_email_with_report(report_path: str) -> bool:
    """Send email with Indonesian format and 3 retry attempts"""
    for attempt in range(3):
        try:
            if not report_path or not os.path.exists(report_path):
                raise FileNotFoundError(f"Report file missing: {report_path}")
            
            msg = MIMEMultipart()
            msg['From'] = SMTP_CONFIG['sender_email']
            msg['To'] = SMTP_CONFIG['recipient_email']
            msg['Subject'] = f"Laporan Regresi Tokopart - {datetime.now().strftime('%d %B %Y')}"
            
            # Indonesian email body
            email_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                    <h2 style="color: #2a5885;">Laporan Automation Testing</h2>
                    <p>Berikut Hasil Regresi Tokopart Terbaru:</p>
                    
                    <ul style="margin-left: 20px; padding-left: 0;">
                        <li><strong>Waktu Generate:</strong> {datetime.now().strftime('%d %B %Y %H:%M')}</li>
                        <li><strong>Scenario:</strong> 
                            <a href="https://docs.google.com/spreadsheets/d/1PaPr6YelsyxuTYe9GVNgv2ztAGLu3WvKS6g8rOXMyHI/edit?gid=1771717336#gid=1771717336" 
                               style="color: #1a73e8; text-decoration: underline;">
                               Link Google Sheets Test Scenario
                            </a>
                        </li>
                        <li><strong>File:</strong> Terlampir ({'PDF Report' if report_path.endswith('.pdf') else 'Error Log'})</li>
                    </ul>
                    
                    <p style="margin-top: 20px; color: #666; font-size: 0.9em;">
                        Email ini dikirim otomatis oleh sistem automation testing Tokopart.
                    </p>
                </body>
            </html>
            """
            
            # Attach report
            if report_path.endswith('.pdf'):
                with open(report_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name="Laporan_Regresi_Tokopart.pdf")
                    part['Content-Disposition'] = 'attachment; filename="Laporan_Regresi_Tokopart.pdf"'
                    msg.attach(part)
            else:
                with open(report_path, "r", encoding='utf-8') as f:
                    part = MIMEText(f.read())
                    part['Content-Disposition'] = 'attachment; filename="Error_Log.txt"'
                    msg.attach(part)
            
            msg.attach(MIMEText(email_body, 'html'))
            
            with smtplib.SMTP(
                host=SMTP_CONFIG['smtp_server'],
                port=SMTP_CONFIG['smtp_port'],
                timeout=SMTP_CONFIG['timeout']
            ) as server:
                server.starttls()
                server.login(SMTP_CONFIG['smtp_username'], SMTP_CONFIG['smtp_password'])
                server.send_message(msg)
                logging.info(f"Email berhasil dikirim ke {SMTP_CONFIG['recipient_email']}")
                return True
                
        except Exception as e:
            logging.warning(f"Percobaan pengiriman email ke-{attempt+1} gagal: {str(e)}")
            if attempt < 2:
                import time
                time.sleep(5)
    
    logging.error("Semua percobaan pengiriman email gagal")
    return False

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Generate and send final report"""
    try:
        if hasattr(session, 'all_test_results'):
            logging.info(f"Memproses {len(session.all_test_results)} hasil test...")
            
            # Generate report (PDF or error file)
            report_path = generate_pdf_report(session.all_test_results)
            
            # Send email if report exists
            if report_path:
                if not send_email_with_report(report_path):
                    logging.error("Gagal mengirim email tetapi laporan berhasil dibuat")
            else:
                logging.error("Gagal membuat laporan")
                
    except Exception as e:
        logging.error(f"Error pada akhir sesi: {str(e)}")
        try:
            with open("reports/errors/FATAL_ERROR.txt", "w", encoding='utf-8') as f:
                f.write(f"Error fatal: {str(e)}\n")
        except:
            pass