from importlib import resources
from pathlib import Path
import logging
import logging.config
import traceback
import sys
import yaml


PGM_DIR = Path("collectlicense")
APP_ID = 'collectlicense'
CMD = None

def load_config():
    global CMD
    logconf_str = resources.read_text('collectlicense','logconf.yml')
    logging.config.dictConfig(yaml.safe_load(logconf_str))
    logger = logging.getLogger('main')
    config_str = resources.read_text('collectlicense','config.yml')
    config = yaml.safe_load(config_str)
    CMD = config['collectlicense']['common']['CMD']
    return config, logger

def mkdirs(dir_path:Path):
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
    if not dir_path.is_dir():
        raise BaseException(f"Don't make diredtory.({str(dir_path)})")
    return dir_path

def e_msg(e:Exception, logger):
    tb = sys.exc_info()[2]
    logger.error(traceback.format_exc())
    return e.with_traceback(tb)

