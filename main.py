import datetime
import os
from pathlib import Path
import re
import shutil
import sqlite3
import yaml

from logger import logger

logger.info('Opening config.yml')
try:
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)
except Exception as e:
    logger.error(f"Failed to open config.yml: {e}")
    raise

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', ' -', filename)

query = '''
SELECT
    a.id
    , a.title
    , a.path
    , b.publisher
    , c.series
    , d.format
    , d.filename
FROM books a
LEFT JOIN (
    SELECT
        x.book
        , y.publisher
    FROM books_publishers_link x
    LEFT JOIN (
    	SELECT
    		id
    		, name AS publisher
    	FROM publishers
    ) y ON x.publisher = y.id
) b ON a.id = b.book
LEFT JOIN (
    SELECT
        book
        , y.series
    FROM books_series_link x
    LEFT JOIN (
    	SELECT
    		id
    		, name AS series
    	FROM series
    ) y ON x.series = y.id
) c ON a.id = c.book
LEFT JOIN (
	SELECT
		book
		, format
        , name AS filename
	FROM data
) d ON a.id = d.book
'''

logger.info('Fetching data from metadata.db')
try:
    with sqlite3.connect(f"{config.get('calibre library path')}/metadata.db".replace('//','/')) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        tables = cursor.fetchall()
except Exception as e:
    logger.error(f"Fetching data from metadata.db failed: {e}")
    raise

# Check if destination path exist
logger.info('Creating destination path')
try:
    if not os.path.exists(config.get('destination root path')):
        os.makedirs(config.get('destination root path'))
except Exception as e:
    logger.error(f"Fetching data from metadata.db failed: {e}")
    raise

library_path = config.get('calibre library path')
destination_root = config.get('destination root path')

logger.info('Copying calibre books to destination path:')
print('')
try:
    for book in tables:
        name = sanitize_filename(book[1])
        path = book[2]
        publisher = sanitize_filename(book[3])
        try:
            series = sanitize_filename(book[4])
        except:
            series = book[4]
        format = book[5].lower()
        filename = book[6]

        series_dir = series if series else '[no series]'
        
        original_path = os.path.join(library_path, path, f"{filename}.{format}")
        destination_path = os.path.join(destination_root, series_dir, f"{name} [{publisher}].{format}").replace(':', ' -')

        logger.info(f"Copying {name}")
        logger.info(f"Source: {original_path}")
        logger.info(f"Destination: {destination_path}")

        try:
            destination_dir = os.path.join(destination_root, series_dir)

            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
        except Exception as e:
            logger.error(f"Failed to create series directory: {e}")
            raise

        try:
            if os.path.exists(destination_path):
                file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(destination_path))
                time_difference = datetime.datetime.now() - file_mod_time

                if time_difference.days < int(config.get('days to overwrite')):
                    shutil.copy2(original_path, destination_path)
                    logger.info(f"Success, file is not older than {config.get('days to overwrite')} days old and overwritten")
                else:
                    logger.info(f"Skipped, file is older than {config.get('days to overwrite')} days old")
                
            else:
                shutil.copy2(original_path, destination_path)
                logger.info('Success')
        
        except Exception as e:
            logger.warning(f"Failed: {e}")
        
        print('')

except Exception as e:
    logger.error(e)
    raise