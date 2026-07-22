import io
import os
import qrcode
from datetime import datetime, timezone
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.utils import ImageReader
 
from app.model.leave_request import LeaveRequest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOGO_PATH = PROJECT_ROOT / "app" / "static" / "logo.png"


def _resolve_logo_path()->Path|None:
    configured_path = os.getenv("LEAVE_PDF_LOGO_PATH")
    logo_path = Path(configured_path) if configured_path else DEFAULT_LOGO_PATH
    if not logo_path.is_absolute():
        logo_path = PROJECT_ROOT / logo_path
    return logo_path if logo_path.exists() else None


def _build_logo_image(max_width=34 * mm, max_height=18 * mm)->Image|None:
    logo_path = _resolve_logo_path()
    if not logo_path:
        return None

    try:
        image_width, image_height = ImageReader(str(logo_path)).getSize()
    except Exception:
        return None

    scale = min(max_width / image_width, max_height / image_height)
    return Image(str(logo_path), width=image_width * scale, height=image_height * scale)

def _generate_qr_code(verification_url:str)->io.BytesIO:
    """
    Generates a QR code image in memory (no file saved to disk).
    Anyone scanning it lands on a verification URL containingf
    the reference number — proves the letter is authentic.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1f36", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def _format_date(d)->str:
    if not d:
        return "-"
    return d.strftime("%B %d, %Y")

def _get_leave_period_text(leave:LeaveRequest)->str:
    if leave.leave_type in ("Sick Leave","Personal Leave"):
        return f"{_format_date(leave.start_date)} to {_format_date(leave.end_date)}"
    elif leave.leave_type == "Emergency Leave":
        return f"{_format_date(leave.leave_date)}"
    elif leave.leave_type == "Half Day Leave":
        return f"{_format_date(leave.leave_date)} ({leave.session}session)"
    return "-"

def generate_approval_letter_pdf(leave:LeaveRequest,
                                 base_verification_url:str="http://157.245.195.23:3001/verify")->io.BytesIO:
    """
    Builds the full Leave Approval Letter PDF in memory and
    returns it as a BytesIO buffer ready to stream to the client.
    """
    buffer=io.BytesIO()
    doc=SimpleDocTemplate(buffer, 
                          pagesize=A4,
                          topMargin=20*mm,
                          bottomMargin=20*mm,
                          leftMargin=22*mm,
                          rightMargin=22*mm)
    styles=getSampleStyleSheet()
    title_style=ParagraphStyle(
        "TitleStyle",parent=styles["Title"],
        fontSize=18,textColor=colors.HexColor("#1a1f36"),
        spaceAfter=2, alignment=TA_LEFT
    )
    subtitle_style=ParagraphStyle(
        "SubtitleStyle",parent=styles["Normal"],
        fontSize=10,textColor=colors.HexColor("#667eea"),
        spaceAfter=14, alignment=TA_LEFT
    )
    section_style=ParagraphStyle(
        "SectionStyle", parent=styles["Heading3"],
        fontSize=11, textColor=colors.HexColor("#667eea"),
        spaceBefore=14, spaceAfter=6,
    )
    body_style=ParagraphStyle(
        "BodyStyle", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#999999"),
        leading=15,
    )
    footer_style=ParagraphStyle(
        "FooterStyle", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#999999"),
        alignment=TA_CENTER,
    )
    elements=[]
    header_text = [
        Paragraph("Sri Lanka Telecom PLC", title_style),
        Paragraph("EmpDiary — Leave Approval Letter", subtitle_style),
    ]
    logo_image = _build_logo_image()
    if logo_image:
        header_table = Table(
            [[logo_image, header_text]],
            colWidths=[42 * mm, 132 * mm],
        )
        header_table.setStyle(TableStyle([
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING",   (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ]))
        elements.append(header_table)
    else:
        elements.extend(header_text)
 
    # ── Reference + Approval Date strip ────────────────────────
    approval = leave.approval[0] if leave.approval else None
    approval_date = approval.decided_at if approval else datetime.now(timezone.utc)
 
    ref_table = Table(
        [[
            Paragraph(f"<b>Reference No.</b><br/>{leave.reference}", body_style),
            Paragraph(f"<b>Approval Date</b><br/>{_format_date(approval_date)}", body_style),
            Paragraph(f"<b>Status</b><br/><font color='#38a169'><b>APPROVED</b></font>", body_style),
        ]],
        colWidths=[58 * mm, 58 * mm, 58 * mm],
    )
    ref_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor("#f8f9fc")),
        ("BOX",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    elements.append(ref_table)
    elements.append(Spacer(1, 14))
 
    # ── Employee Information ───────────────────────────────────
    elements.append(Paragraph("Employee Information", section_style))
    emp_table = Table(
        [
            ["Full Name",  leave.user.name],
            ["Email",      leave.user.email],
            ["Phone",      leave.user.phone or "—"],
        ],
        colWidths=[40 * mm, 134 * mm],
    )
    emp_table.setStyle(TableStyle([
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",    (0, 0), (0, -1), colors.HexColor("#888888")),
        ("TEXTCOLOR",    (1, 0), (1, -1), colors.HexColor("#333333")),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 2),
    ]))
    elements.append(emp_table)
 
    # ── Leave Information ──────────────────────────────────────
    elements.append(Paragraph("Leave Information", section_style))
    leave_table = Table(
        [
            ["Leave Type",  leave.leave_type],
            ["Period",      _get_leave_period_text(leave)],
            ["Reason",      leave.reason],
        ],
        colWidths=[40 * mm, 134 * mm],
    )
    leave_table.setStyle(TableStyle([
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",    (0, 0), (0, -1), colors.HexColor("#888888")),
        ("TEXTCOLOR",    (1, 0), (1, -1), colors.HexColor("#333333")),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 2),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(leave_table)
 
    # ── Supervisor Information ─────────────────────────────────
    elements.append(Paragraph("Approved By", section_style))
    sup_table = Table(
        [
            ["Supervisor",  leave.supervisor.name],
            ["Email",       leave.supervisor.email],
            ["Comments",     approval.comments if approval and approval.comments else "—"],
        ],
        colWidths=[40 * mm, 134 * mm],
    )
    sup_table.setStyle(TableStyle([
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",    (0, 0), (0, -1), colors.HexColor("#888888")),
        ("TEXTCOLOR",    (1, 0), (1, -1), colors.HexColor("#333333")),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 2),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(sup_table)
 
    elements.append(Spacer(1, 20))
 
    # ── QR Code + verification note ────────────────────────────
    verification_url = f"{base_verification_url}/{leave.reference}"
    qr_buffer = _generate_qr_code(verification_url)
    qr_image  = Image(qr_buffer, width=28 * mm, height=28 * mm)
 
    qr_table = Table(
        [[
            qr_image,
            Paragraph(
                f"<b>Verification</b><br/>"
                f"Scan this QR code or visit the link below to verify "
                f"this letter's authenticity.<br/>"
                f"<font color='#667eea'>{verification_url}</font>",
                body_style,
            ),
        ]],
        colWidths=[35 * mm, 139 * mm],
    )
    qr_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(qr_table)
 
    elements.append(Spacer(1, 30))
 
    # ── Footer ──────────────────────────────────────────────────
    elements.append(Paragraph(
        "This is a system-generated document from EmpDiary — SLT Mobitel "
        "Employee Management System. No physical signature is required.",
        footer_style,
    ))
 
    doc.build(elements)
    buffer.seek(0)
    return buffer
