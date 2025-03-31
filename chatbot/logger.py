import logging


from configs import configs


_LEVEL = configs.LOG_LEVEL or logging.DEBUG # Default to DEBUG if not set in configs

# Configure logging
logging.basicConfig(level=_LEVEL, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)