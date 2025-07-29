from sqlite3 import Cursor
from typing import Optional
from sqlazo import Database
from chromologger import Logger as Log

log: Log = Log('./log.log')

def database_config():
    db: Database = Database('./database/config.db', False)
    # Query to validate that the table exists
    validate_query: Optional[Cursor] = db.get_data_where('config_ui', 'id == 1')

    # Means that database don't have configs
    # Create initial configs
    if validate_query is None:
        cols_config: list[str] = ['id INTEGER PRIMARY KEY', 'name TEXT NOT NULL', 'value TEXT NOT NULL']
        db.create_table('config_ui', cols_config)
        db.insert_data(['current_lang_code', 'es_CO'], ['name', 'value'], 'config_ui')
        db.insert_data(['last_directory_open', 'C:/'], ['name', 'value'], 'config_ui')
        db.insert_data(['last_directory_output', 'C:/'], ['name', 'value'], 'config_ui')
        db.insert_data(['max_file_size', 10*1024*1024], ['name', 'value'], 'config_ui')
