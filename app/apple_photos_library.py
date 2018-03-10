import os
import sqlite3
import shutil


SUBPATH_TO_PHOTOS_DB = 'database/photos.db'
SUBPATH_TO_PHOTOS = 'Masters'
TMP_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'tmp')


def dump_image_paths(photos_library_path, destination_filepath, limit=None):
    # the database is locked, so it needs to copied just to be queried
    source_db_path = os.path.join(photos_library_path, SUBPATH_TO_PHOTOS_DB)
    temp_db_path = os.path.join(TMP_DIRECTORY, 'dupe_photos.db')
    # ensure spaces in filepath names are appropriately escaped
    photos_library_path = photos_library_path.replace('\ ', ' ').replace(' ', '\ ')
    shutil.copyfile(source_db_path, temp_db_path)

    # query the database for image subpaths
    query = """SELECT imagePath FROM RKMaster"""
    if limit:
        query += f" LIMIT {limit}"
    db_connection = sqlite3.connect(temp_db_path)
    db_cursor = db_connection.cursor()
    db_cursor.execute(query)

    # dump the full image paths to the destination_filepath
    photo_file_basepath = os.path.join(photos_library_path, SUBPATH_TO_PHOTOS).replace('\ ', ' ')
    with open(destination_filepath, 'w') as f:
        for query_result in db_cursor:
            f.write(os.path.join(photo_file_basepath, query_result[0]) + '\n')
