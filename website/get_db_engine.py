import chartly.settings as settings
import sqlalchemy
from urllib import quote_plus as urlquote

def get_db_engine(db_name = 'write_to'):
    """
    Emits a SQL alchemy engine from the settings file
    """
    db = settings.CUSTOM_DATABASES[db_name]
    engine_string = '%s://%s:%s@%s:%s/%s' % (
            db['ENGINE'].split('.')[-1].lower(), 
            db['USER'],
            urlquote(db['PASSWORD']),
            db['HOST'], 
            db['PORT'], 
            db['NAME'])
    return sqlalchemy.create_engine(engine_string,)