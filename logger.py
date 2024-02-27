import logging
import os
import re

BASE_DIR = os.path.dirname(__file__)

TEST = re.search("root", BASE_DIR) is not None

FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
FILENAME = "/var/log/hearts/log"

logging.basicConfig(
    format=FORMAT,
    filename=FILENAME,
    level=logging.DEBUG if TEST else logging.INFO,
)
logger = logging.getLogger()
