import asyncio

from celery import current_task
from celery.utils.log import get_task_logger
from .celery_app import celery_app
from paper_trade.ema9_ha import ema9_ha
from paper_trade.mis import process

logger = get_task_logger(__name__)

@celery_app.task
def mis_paper(config) -> dict:
    logger.info("mis called")
    process(config)
    return {'result': config}


