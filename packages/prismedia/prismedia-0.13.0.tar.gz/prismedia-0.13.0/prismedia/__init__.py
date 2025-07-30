from future import standard_library
standard_library.install_aliases()
import logging
logger = logging.getLogger('Prismedia')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

from . import upload
