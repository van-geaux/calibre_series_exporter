#!/usr/bin/env python3

import logging
import os
import shutil
import sqlite3
import sys
import yaml

from datetime import datetime
from pathlib import Path

def set_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    files = list(Path('logs/').iterdir())
    files = [f for f in files if f.is_file()]
    if len(files) > 10:
        files.sort(key=lambda f: f.stat().st_mtime)
        oldest_file = files[0]
        os.remove(oldest_file)
        print(f"Deleted: {oldest_file}")
    else:
        pass

    with open('config.yml', 'r', encoding='utf-8') as file:
        config_content = file.read()
        config = yaml.safe_load(config_content)

    try:
        log_level_str = config.get('log_level', 'INFO').upper()
    except:
        log_level_str = 'INFO'

    log_level_console = getattr(logging, log_level_str, logging.INFO)
    log_level_file = getattr(logging, log_level_str, logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level_console)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(f"logs/app-{datetime.now().date().isoformat().replace('-', '')}.log", encoding='utf-8')
    file_handler.setLevel(log_level_file)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

def get_config() -> dict:
    default_content = """
# metadata.db location
calibre library path: '/volume1/data/media/books/calibre'

destination root path: '/volume1/data/media/books/calibre_series'

# every books without a series will be put here
one shot folder name: '_oneshots'

# Console default to info, file default to warning. Set to change both
log level: 
"""
    print('Opening config.yml')
    try:
        with open('config.yml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except Exception:
        with open('config.yml', 'w', encoding='utf-8') as env_file:
            env_file.write(default_content)
        print(f"{'config.yml'} created, if you haven't set your config then please put them in the config.yml then rerun the script")
        sys.exit()

def sanitize_filename(filename: str) -> str:
    if not filename:
        return 'no_name'
    filename = filename.replace(": ", " - ").replace(":", "-").replace("/", "-").replace("\\", "-")
    filename = filename.replace("*", "-").replace("?", "").replace('"', "")
    filename = filename.replace("<", "-").replace(">", "-").replace("|", "-")
    filename = filename.rstrip('.')
    return filename

def fetch_book_data(config: dict) -> dict:
    logger.info('Fetching data from metadata.db')
    try:
        with sqlite3.connect(f"{config.get('calibre library path')}/metadata.db".replace('//','/')) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                SELECT
                    a.id
                    , a.title
                    , a.path
                    , c.name AS series_title
                    , a.series_index
                    , d.format
                    , d.name AS filename
                    , a.last_modified
                FROM books a
                LEFT JOIN (
                    SELECT * FROM books_series_link x
                    LEFT JOIN series y ON x.series = y.id
                ) c ON a.id = c.book
                LEFT JOIN data d ON a.id = d.book
            ''')
            rows = cursor.fetchall()
        data_table = []
        for row in rows:
            id, title, path, series_title, series_index, format, filename, last_modified = row
            data_table.append({'id': id
                               , 'title': title
                               , 'path': path
                               , 'series_title': series_title
                               , 'series_index': series_index
                               , 'format': format
                               , 'filename': filename
                               , 'last_modified': last_modified})
        return data_table
    
    except Exception as e:
        logger.error(f"Fetching data from metadata.db failed: {e}")
        sys.exit(1)

def clear_broken_link(destination_root: str) -> None:
    removed_links = []
    
    for root, _, files in os.walk(destination_root):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.stat(file_path)
            except FileNotFoundError:
                os.remove(file_path)
                removed_links.append(file_path)

    logger.info(f"Removed {len(removed_links)} broken hard links.")
    if removed_links:
        logger.info("\nRemoved links:")
        for link in removed_links:
            logger.warning(link)

    # remove empty
    for root, dirs, _ in os.walk(destination_root, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                os.rmdir(dir_path)
                logger.info(f"Removed empty folder: {dir_path}")
            except OSError:
                pass

    for root, dirs, _ in os.walk(destination_root, topdown=False):
        for dir_name in dirs:
            keyword = 'TailCharacterConflict'
            if keyword in dir_name:
                folder_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(folder_path)
                    logger.info(f"Removed broken folder: {folder_path}")
                except OSError as e:
                    logger.info(f"Error removing broken folder: {folder_path}: {e}")

def create_link(config: dict, data_table:list, library_path:str, destination_root: str) -> None:
    logger.info('Checking destination path')
    try:
        if not os.path.exists(destination_root):
            os.makedirs(destination_root)
    except Exception as e:
        logger.error(f"Checking destination path failed: {e}")
        sys.exit(1)

    logger.info('Linking calibre books to destination path:')
    print('')
    try:
        new_links = []
        updated_links = []
        for book in data_table:
            name = sanitize_filename(book['title'])
            book_path = book['path']

            try:
                series_title = sanitize_filename(book['series_title'])
            except:
                series_title = book['series_title']

            format = book['format'].lower()
            filename = book['filename']

            series_dir = series_title if series_title != 'no_name' else config.get('one shot folder name')
            original_path = os.path.join(library_path, book_path, f"{filename}.{format}")

            destination_path = os.path.join(destination_root, series_dir, f"{name}.{format}")

            logger.debug(f"Creating hardlink for {name}")
            logger.debug(f"Source: {original_path}")
            logger.debug(f"Destination: {destination_path}")

            try:
                destination_dir = os.path.join(destination_root, series_dir)
                if not os.path.exists(destination_dir):
                    os.makedirs(destination_dir)
            except Exception as e:
                logger.error(f"Failed to create series directory: {e}")
                sys.exit(1)

            try:
                os.link(original_path, destination_path)
                new_links.append(destination_path)
                logger.debug(f"Created new link")
            except FileExistsError:
                if os.path.getmtime(original_path) > os.path.getmtime(destination_path):
                    os.remove(destination_path)
                    os.link(original_path, destination_path)
                    logger.debug(f"Created new link")
                    updated_links.append(destination_path)
                else:
                    logger.debug(f"New link is not needed")
            except Exception as e:
                logger.error(f"Failed to link file: {e}")

        logger.info(f"Created {len(new_links)} new links.")
        if new_links:
            logger.info("\nNew links:")
            for link in new_links:
                logger.info(link)
            print('')

        logger.info(f"Updated {len(updated_links)} old links.")
        if updated_links:
            logger.info("\nUpdated links:")
            for link in updated_links:
                logger.info(link)
            print('')

    except Exception as e:
        logger.error(e)
        sys.exit(1)

def delete_series_book(config: dict, data_table: list, destination_root: str):
    # delete disrepancy in series name vs series folder
    existing_folders = [f for f in os.listdir(destination_root) if os.path.isdir(os.path.join(destination_root, f))]
    existing_series = list({sanitize_filename(item['series_title']) for item in data_table if sanitize_filename(item['series_title']) != 'no_name'})
    removed_folder = []
    for folder in existing_folders:
        if folder != config.get('one shot folder name') and folder not in existing_series:
            print(f'folder to be deleted: {folder}')
            removed_folder.append(folder)
            shutil.rmtree(os.path.join(destination_root, folder))

    logger.info(f"Removed {len(removed_folder)} mismatched folders.")
    if removed_folder:
        logger.info("\Removed folders:")
        for removedf in removed_folder:
            logger.info(removedf)
        print('')

    # delete disrepancy in title vs file name
    existing_folders = [f for f in os.listdir(destination_root) if os.path.isdir(os.path.join(destination_root, f))]
    removed_file = []
    for folder in existing_folders:
        series_root = os.path.join(destination_root, folder)
        folder_files = [f for f in os.listdir(series_root) if os.path.isfile(os.path.join(series_root, f))]
        for file in folder_files:
            if folder == config.get('one shot folder name'):
                series_name = 'no_name'
            else:
                series_name = folder

            series_books = [sanitize_filename(item.get('title')) +'.'+ item['format'].lower() for item in data_table if sanitize_filename(item.get('series_title')) == series_name]
            if file not in series_books:
                if series_name == 'no_name':
                    removed_file.append(os.path.join(folder, file).replace('no_name', config.get('one shot folder name')))
                    os.remove(os.path.join(destination_root, config.get('one shot folder name'), file))
                else:
                    removed_file.append(os.path.join(folder, file))
                    os.remove(os.path.join(destination_root, series_name, file))
    
    logger.info(f"Removed {len(removed_file)} mismatched files.")
    if removed_file:
        logger.info("\Removed files:")
        for removedt in removed_file:
            logger.info(removedt)
        print('')


if __name__ == "__main__":
    config = get_config()
    logger = set_logger()

    library_path = config.get('calibre library path')
    destination_root = config.get('destination root path')

    data_table = fetch_book_data(config)
    
    create_link(config, data_table, library_path, destination_root)
    clear_broken_link(destination_root)
    delete_series_book(config, data_table, destination_root)

    print('')
    logger.info('Finished')