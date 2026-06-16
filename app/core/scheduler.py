from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.db.database import SessionLocal
from app.services import medical_certificate_service
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
 
    scheduler.start()
    logger.info("Background scheduler started.")
    return scheduler        