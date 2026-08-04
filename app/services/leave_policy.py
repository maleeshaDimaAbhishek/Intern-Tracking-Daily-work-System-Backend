from datetime import date


MEDICAL_CERTIFICATE_THRESHOLD_DAYS = 2


def requires_medical_certificate(
    leave_type: str,
    start_date: date | None,
    end_date: date | None,
) -> bool:
    """Return whether a leave spans enough calendar days to require a certificate."""
    if leave_type != "Sick Leave" or start_date is None or end_date is None:
        return False

    # Both the first and last day are leave days. For example, Monday through
    # Tuesday is two days and does not require a certificate; Monday through
    # Wednesday is three days and does.
    duration_days = (end_date - start_date).days + 1
    return duration_days > MEDICAL_CERTIFICATE_THRESHOLD_DAYS


def get_leave_period(
    leave_type: str,
    start_date: date | None,
    end_date: date | None,
    leave_date: date | None,
) -> tuple[date, date]:
    """Normalize every leave type to an inclusive start/end period."""
    if leave_type in ("Sick Leave", "Personal Leave"):
        if start_date is None or end_date is None:
            raise ValueError("Range leave requires start and end dates.")
        return start_date, end_date

    if leave_date is None:
        raise ValueError("Single-day leave requires a leave date.")
    return leave_date, leave_date
