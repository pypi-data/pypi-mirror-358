from .database import Manager
from chromologger import Logger as Log

# Initial paths to files
log:Log = Log('PYMD/logs/log_pymd.log')

class Pymd:
    @staticmethod
    def run_app():
        try:
            Manager.database_config()
            from .interface import run
            run()
        except Exception as e:
            log.log_e(e)