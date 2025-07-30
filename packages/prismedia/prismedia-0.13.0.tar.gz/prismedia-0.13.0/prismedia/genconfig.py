from os.path import join, abspath, isfile, dirname, exists
from os import listdir
from shutil import copyfile
import logging
logger = logging.getLogger('Prismedia')

from . import utils


def genconfig():
    path = join(dirname(__file__), 'config')
    files = [f for f in listdir(path) if isfile(join(path, f))]

    for f in files:
        final_f = f.replace(".sample", "")
        if exists(final_f) and not utils.ask_overwrite(final_f + " already exists. Do you want to overwrite it?"):
            continue

        copyfile(join(path, f), final_f)
        logger.info(str(final_f) + " correctly generated, you may now edit it to fill your credentials.")


if __name__ == '__main__':
    genconfig()
