import os
import re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(test_item):
    """Generate individual PDF report for a single test"""
    try:
        # Get test information
        test_name = test_item.nodeid.split('::')[-1]
        test_status = getattr(test_item, '_test_status', 'UNKNOWN').upper()
        screenshot_path = getattr(test_item, '_screenshot_path', None)
        
        # Setup PDF file
        pdf_dir = r"C:\Testing\Automation Python\Tokopart\reports\pdf"
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"report_{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        # Create styles
        styles = getSampleStyleSheet()
        status_style = ParagraphStyle(
            'StatusStyle',
            parent=styles['Heading2'],
            textColor=colors.green if test_status == 'PASSED' else colors.red,
            spaceAfter=20
        )
        
        # Build PDF content
        elements = [
            Paragraph("TOKOPART TEST REPORT", styles['Title']),
            Spacer(1, 20),
            Paragraph(f"Test Case: {test_name}", styles['Heading2']),
            Paragraph(f"Status: {test_status}", status_style),
            Spacer(1, 20)
        ]
        
        # Add screenshot if available
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                img = Image(screenshot_path)
                img.drawWidth = 500
                img.drawHeight = 300
                elements.extend([
                    Paragraph("TEST EVIDENCE:", styles['Heading3']),
                    Spacer(1, 10),
                    img
                ])
            except Exception as e:
                elements.append(Paragraph(f"Failed to load screenshot: {str(e)}", styles['Italic']))
        
        # Generate PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        doc.build(elements)
        
    except Exception as e:
        print(f"Failed to generate PDF report: {str(e)}")
        raise

def generate_consolidated_pdf_report(test_results):
    """Generate consolidated PDF report for all tests"""
    try:
        # Setup PDF file
        pdf_dir = r"C:\Testing\Automation Python\Tokopart\reports\pdf"
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"regression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        # Create styles
        styles = getSampleStyleSheet()
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
        
        # Start building PDF
        elements = [
            Paragraph("TOKOPART REGRESSION TEST REPORT", styles['Title']),
            Spacer(1, 20),
            Paragraph(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']),
            Spacer(1, 30)
        ]
        
        # Add each test result
        for test in test_results:
            # Test header with status
            status_style = 'PassedStyle' if test['status'] == 'PASSED' else 'FailedStyle'
            elements.append(Paragraph(f"Test Case: {test['name']}", styles['Heading2']))
            elements.append(Paragraph(f"Status: {test['status']}", styles[status_style]))
            elements.append(Paragraph(f"Duration: {test['duration']:.2f}s", styles['Normal']))
            
            # Add error message if failed
            if test['status'] == 'FAILED' and test['error']:
                elements.append(Paragraph("Error Details:", styles['Heading3']))
                elements.append(Paragraph(test['error'], styles['Code']))
            
            # Add screenshot if available
            if test['screenshot_path'] and os.path.exists(test['screenshot_path']):
                try:
                    img = Image(test['screenshot_path'])
                    img.drawWidth = 500
                    img.drawHeight = 300
                    elements.extend([
                        Spacer(1, 10),
                        Paragraph("Screenshot:", styles['Heading3']),
                        Spacer(1, 5),
                        img,
                        Spacer(1, 20)
                    ])
                except Exception as e:
                    elements.append(Paragraph(f"Screenshot load error: {str(e)}", styles['Italic']))
            else:
                elements.append(Paragraph("No screenshot available", styles['Italic']))
            
            elements.append(Spacer(1, 30))
        
        # Generate PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        doc.build(elements)
        print(f"Consolidated PDF report generated: {pdf_path}")
        
    except Exception as e:
        print(f"Failed to generate consolidated report: {str(e)}")
        raise