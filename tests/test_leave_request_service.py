from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.schemas.leave_request import LeaveRequestCreate
from app.services import leave_request_service


def _schema() -> LeaveRequestCreate:
    tomorrow = date.today() + timedelta(days=1)
    return LeaveRequestCreate(
        leave_type="Emergency Leave",
        reason="A valid emergency leave reason",
        emergency_contact="+94771234567",
        supervisor_id=7,
        leave_date=tomorrow,
    )


def test_submit_rejects_new_request_when_user_has_pending_leave():
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(id=7)
    pending = SimpleNamespace(reference="LR-PENDING")

    with (
        patch.object(
            leave_request_service.leave_request_repo,
            "get_pending_leave_request",
            return_value=pending,
        ),
        patch.object(
            leave_request_service.leave_request_repo,
            "get_overlapping_leave_request",
        ) as overlap_check,
        patch.object(
            leave_request_service.leave_request_repo,
            "create_leave_request",
        ) as create_leave,
    ):
        with pytest.raises(HTTPException) as error:
            leave_request_service.submit_leave_request(db, 42, _schema())

    assert error.value.status_code == 409
    assert "already have a pending leave request" in error.value.detail
    assert "LR-PENDING" in error.value.detail
    overlap_check.assert_not_called()
    create_leave.assert_not_called()
