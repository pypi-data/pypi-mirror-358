import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

file_handler = logging.FileHandler("tree.log", mode='w')
stream_handler = logging.StreamHandler(stream=sys.stdout)

file_handler.setLevel(level=logging.DEBUG)
stream_handler.setLevel(level=logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
