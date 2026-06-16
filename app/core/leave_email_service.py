"""
leave_email_service.py

All leave-related email functions.
Builds on top of the existing _send_email() helper
already in email_service.py.
"""
from app.core.email_service import _send_email


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def _format_date(d) -> str:
    """Safely format a date or return dash"""
    if not d:
        return "—"
    try:
        return d.strftime("%B %d, %Y")
    except Exception:
        return str(d)


def _get_date_info(leave: dict) -> str:
    """
    Build the date line based on leave type.
    Accepts a plain dict with leave fields.
    """
    leave_type = leave.get("leave_type", "")

    if leave_type in ("Sick Leave", "Personal Leave"):
        return (
            f"From <strong>{_format_date(leave.get('start_date'))}</strong> "
            f"to <strong>{_format_date(leave.get('end_date'))}</strong>"
        )
    elif leave_type == "Emergency Leave":
        return f"Date: <strong>{_format_date(leave.get('leave_date'))}</strong>"
    elif leave_type == "Half Day Leave":
        session = leave.get("session", "—")
        return (
            f"Date: <strong>{_format_date(leave.get('leave_date'))}</strong> "
            f"({session})"
        )
    return "—"


def _base_card(content: str) -> str:
    """Shared email wrapper — consistent look for all leave emails"""
    return f"""
    <div style="font-family:'Segoe UI',sans-serif;max-width:560px;
                margin:auto;padding:2rem;border:1px solid #e2e8f0;
                border-radius:16px;background:#fff;">
      <div style="text-align:center;margin-bottom:1.5rem;">
        <h1 style="font-size:2rem;margin:0;">📋</h1>
        <h2 style="color:#667eea;margin:0.5rem 0 0.2rem;">EmpDiary</h2>
        <p style="color:#888;font-size:0.85rem;margin:0;">Leave Management System</p>
      </div>
      {content}
      <p style="color:#aaa;font-size:0.75rem;text-align:center;margin-top:2rem;">
        This is an automated message. Do not reply to this email.
      </p>
    </div>
    """


# ──────────────────────────────────────────────────────────────
# EMAIL 1 — Supervisor notified of new request
# ──────────────────────────────────────────────────────────────

def send_leave_submitted_email(
    supervisor_email: str,
    supervisor_name:  str,
    employee_name:    str,
    leave: dict,
) -> None:
    subject = f"New Leave Request from {employee_name}"
    content = f"""
    <p style="color:#333;">Hi <strong>{supervisor_name}</strong>,</p>
    <p style="color:#555;line-height:1.6;">
      <strong>{employee_name}</strong> has submitted a leave request
      that requires your review.
    </p>
    <div style="background:#f8f9fc;border-radius:12px;
                padding:1.2rem 1.5rem;margin:1.2rem 0;
                border-left:4px solid #667eea;">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;width:140px;">Leave Type</td>
          <td style="padding:0.4rem 0;color:#333;font-weight:600;">{leave.get('leave_type')}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Date(s)</td>
          <td style="padding:0.4rem 0;color:#333;">{_get_date_info(leave)}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Reference</td>
          <td style="padding:0.4rem 0;color:#667eea;font-weight:700;
                     font-family:monospace;">{leave.get('reference_number')}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Reason</td>
          <td style="padding:0.4rem 0;color:#555;">{leave.get('reason')}</td>
        </tr>
      </table>
    </div>
    <p style="color:#555;">Please log in to EmpDiary to review and action this request.</p>
    """
    _send_email(supervisor_email, subject, _base_card(content))


# ──────────────────────────────────────────────────────────────
# EMAIL 2 — Employee notified of approval
# ──────────────────────────────────────────────────────────────

def send_leave_approved_email(
    employee_email:  str,
    employee_name:   str,
    supervisor_name: str,
    leave: dict,
) -> None:
    subject = f"✅ Your {leave.get('leave_type')} Request Has Been Approved"

    medical_note = ""
    if leave.get("leave_type") == "Sick Leave":
        medical_note = """
        <div style="background:#fffbeb;border:1px solid #fcd34d;
                    border-radius:8px;padding:0.9rem 1rem;margin-top:1rem;">
          <p style="margin:0;color:#92400e;font-size:0.85rem;">
            ⚠️ <strong>Medical Certificate Required:</strong>
            Please upload your medical certificate within
            <strong>14 days</strong> from your leave end date.
            Failure to do so will mark your certificate as overdue.
          </p>
        </div>
        """

    content = f"""
    <p style="color:#333;">Hi <strong>{employee_name}</strong>,</p>
    <p style="color:#555;line-height:1.6;">
      Great news! Your leave request has been
      <strong style="color:#38a169;">approved</strong>
      by <strong>{supervisor_name}</strong>.
    </p>
    <div style="background:#f0fff4;border-radius:12px;
                padding:1.2rem 1.5rem;margin:1.2rem 0;
                border-left:4px solid #38a169;">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;width:140px;">Leave Type</td>
          <td style="padding:0.4rem 0;color:#333;font-weight:600;">{leave.get('leave_type')}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Date(s)</td>
          <td style="padding:0.4rem 0;color:#333;">{_get_date_info(leave)}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Reference</td>
          <td style="padding:0.4rem 0;color:#667eea;font-weight:700;
                     font-family:monospace;">{leave.get('reference_number')}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Approved by</td>
          <td style="padding:0.4rem 0;color:#333;font-weight:600;">{supervisor_name}</td>
        </tr>
      </table>
    </div>
    {medical_note}
    <p style="color:#555;">
      You can download your approval letter from EmpDiary.
    </p>
    """
    _send_email(employee_email, subject, _base_card(content))


# ──────────────────────────────────────────────────────────────
# EMAIL 3 — Employee notified of rejection
# ──────────────────────────────────────────────────────────────

def send_leave_rejected_email(
    employee_email:  str,
    employee_name:   str,
    supervisor_name: str,
    leave: dict,
    comment: str | None,
) -> None:
    subject = f"❌ Your {leave.get('leave_type')} Request Was Not Approved"

    comment_block = ""
    if comment:
        comment_block = f"""
        <div style="background:#fff5f5;border:1px solid #fed7d7;
                    border-radius:8px;padding:0.9rem 1rem;margin-top:1rem;">
          <p style="margin:0;color:#c53030;font-size:0.85rem;">
            💬 <strong>Supervisor's Comment:</strong> {comment}
          </p>
        </div>
        """

    content = f"""
    <p style="color:#333;">Hi <strong>{employee_name}</strong>,</p>
    <p style="color:#555;line-height:1.6;">
      Unfortunately, your leave request has been
      <strong style="color:#e53e3e;">rejected</strong>
      by <strong>{supervisor_name}</strong>.
    </p>
    <div style="background:#fff5f5;border-radius:12px;
                padding:1.2rem 1.5rem;margin:1.2rem 0;
                border-left:4px solid #e53e3e;">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;width:140px;">Leave Type</td>
          <td style="padding:0.4rem 0;color:#333;font-weight:600;">{leave.get('leave_type')}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Reference</td>
          <td style="padding:0.4rem 0;color:#667eea;font-weight:700;
                     font-family:monospace;">{leave.get('reference_number')}</td>
        </tr>
      </table>
    </div>
    {comment_block}
    <p style="color:#555;">
      If you believe this was a mistake, please contact your supervisor directly.
    </p>
    """
    _send_email(employee_email, subject, _base_card(content))


# ──────────────────────────────────────────────────────────────
# EMAIL 4 — Medical reminder at 7 days
# ──────────────────────────────────────────────────────────────

def send_medical_reminder_email(
    employee_email: str,
    employee_name:  str,
    leave: dict,
    days_remaining: int,
    reminder_number: int,
) -> None:
    urgency_color = "#d69e2e" if reminder_number == 1 else "#e53e3e"
    urgency_label = "Reminder" if reminder_number == 1 else "⚠️ Final Reminder"

    subject = (
        f"{urgency_label}: Medical Certificate Required — "
        f"{days_remaining} day(s) remaining"
    )

    content = f"""
    <p style="color:#333;">Hi <strong>{employee_name}</strong>,</p>
    <p style="color:#555;line-height:1.6;">
      This is reminder <strong>#{reminder_number}</strong>.
      Your approved Sick Leave requires a medical certificate
      to be submitted within <strong>14 days</strong> of your leave end date.
    </p>
    <div style="background:#fffbeb;border-radius:12px;
                padding:1.2rem 1.5rem;margin:1.2rem 0;
                border-left:4px solid {urgency_color};">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;width:160px;">Reference</td>
          <td style="padding:0.4rem 0;color:#667eea;font-weight:700;
                     font-family:monospace;">{leave.get('reference_number')}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Leave Period</td>
          <td style="padding:0.4rem 0;color:#333;">{_get_date_info(leave)}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Days Remaining</td>
          <td style="padding:0.4rem 0;font-weight:700;color:{urgency_color};">
            {days_remaining} day(s)
          </td>
        </tr>
      </table>
    </div>
    <p style="color:#555;">
      Please log in to EmpDiary and upload your medical certificate
      before the deadline to avoid it being marked as <strong>Overdue</strong>.
    </p>
    """
    _send_email(employee_email, subject, _base_card(content))


# ──────────────────────────────────────────────────────────────
# EMAIL 5 — Medical certificate overdue
# ──────────────────────────────────────────────────────────────

def send_medical_overdue_email(
    employee_email: str,
    employee_name:  str,
    leave: dict,
) -> None:
    subject = "🚨 Medical Certificate Overdue"
    content = f"""
    <p style="color:#333;">Hi <strong>{employee_name}</strong>,</p>
    <p style="color:#555;line-height:1.6;">
      The deadline to submit your medical certificate for your
      approved Sick Leave has <strong style="color:#e53e3e;">passed</strong>.
      Your certificate status has been marked as <strong>Overdue</strong>.
    </p>
    <div style="background:#fff5f5;border-radius:12px;
                padding:1.2rem 1.5rem;margin:1.2rem 0;
                border-left:4px solid #e53e3e;">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;width:140px;">Reference</td>
          <td style="padding:0.4rem 0;color:#667eea;font-weight:700;
                     font-family:monospace;">{leave.get('reference_number')}</td>
        </tr>
        <tr>
          <td style="padding:0.4rem 0;color:#888;font-size:0.85rem;">Leave Period</td>
          <td style="padding:0.4rem 0;color:#333;">{_get_date_info(leave)}</td>
        </tr>
      </table>
    </div>
    <p style="color:#555;">
      Please contact your supervisor or HR department immediately.
    </p>
    """
    _send_email(employee_email, subject, _base_card(content))