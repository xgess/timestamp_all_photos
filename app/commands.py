import os

import click

from . import apple_photos_library


TMP_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'tmp')
FILE_PATH_OF_FILE_PATHS = os.path.join(TMP_DIRECTORY, 'file_paths_to_hashify.txt')
LIMIT = 100


@click.group()
def cli():
    pass


@click.command()
@click.option('--library',
    type=click.Path(exists=True),
    default='/Users/me/Pictures/Photos Library.photoslibrary/',
    help='path to photos library object'
)
def import_photos(library):
    click.echo("Extracting and dumping paths of every photo from your Photos Library...")
    apple_photos_library.dump_image_paths(library, FILE_PATH_OF_FILE_PATHS, limit=LIMIT)


cli.add_command(import_photos)
