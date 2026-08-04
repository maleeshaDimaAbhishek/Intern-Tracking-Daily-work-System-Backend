from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.db.database import SessionLocal
from app.services import medical_certificate_service, pending_leave_cleanup_service
import logging
 
logger = logging.getLogger(__name__)
 
def check_medical_certificates():
    """
    Job that runs daily.
    Opens its own DB session — schedulers run outside
    the normal FastAPI request/response cycle so they
    can't use Depends(get_db).
    """
    db = SessionLocal()
    try:
        results = medical_certificate_service.run_medical_certificate_checks(db)
        logger.info(
            f"Medical cert check complete: "
            f"{results['checked']} checked, "
            f"{results['reminder1_sent']} reminder1 sent, "
            f"{results['reminder2_sent']} reminder2 sent, "
            f"{results['marked_overdue']} marked overdue."
        )
    except Exception as e:
        logger.error(f"Medical cert check failed: {e}")
    finally:
        db.close()


def delete_expired_pending_leaves():
    """Daily job that removes pending requests after their leave date has passed."""
    db = SessionLocal()
    try:
        results = pending_leave_cleanup_service.delete_expired_pending_leaves(db)
        logger.info(
            "Pending leave cleanup complete: %s request(s) deleted for %s.",
            results["deleted"],
            results["checked_on"],
        )
    except Exception:
        db.rollback()
        logger.exception("Pending leave cleanup failed.")
    finally:
        db.close()


def start_scheduler():
    """
    Call this from main.py on app startup.
    """
    scheduler = BackgroundScheduler()
 
    scheduler.add_job(
        check_medical_certificates,
        trigger=CronTrigger(hour=8, minute=0),  # runs every day at 8:00 AM
        id="medical_cert_check",
        replace_existing=True,
    )

    scheduler.add_job(
        delete_expired_pending_leaves,
        trigger=CronTrigger(hour=8, minute=0),
        id="expired_pending_leave_cleanup",
        replace_existing=True,
    )
 
    scheduler.start()
    logger.info("Background scheduler started.")
    return scheduler
