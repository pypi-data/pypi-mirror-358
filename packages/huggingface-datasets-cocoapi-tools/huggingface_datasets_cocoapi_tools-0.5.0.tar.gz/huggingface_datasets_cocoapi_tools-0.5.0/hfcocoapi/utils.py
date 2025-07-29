import logging

logger = logging.getLogger(__name__)

try:
    from tqdm.auto import tqdm
except ImportError:
    logger.warning("tqdm is not installed. Install it to get the progress bar.")

    def tqdm(*args, **kwargs):
        return args[0]
