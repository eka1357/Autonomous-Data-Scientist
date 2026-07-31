"""Worker module package"""
from app.worker.celery_app import celery_app
import app.worker.tasks  # noqa: F401

__all__ = ["celery_app"]

