import os

import click

from .apple_photos_library import dump_image_paths
from .read_and_hashify import read_and_hashify


TMP_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'tmp')
FILE_PATH_OF_FILE_PATHS = os.path.join(TMP_DIRECTORY, 'file_paths_to_hashify.txt')
FILE_PATH_OF_HASHES = os.path.join(TMP_DIRECTORY, 'hashes.txt')
LIMIT = 1000


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
    dump_image_paths(library, FILE_PATH_OF_FILE_PATHS, limit=LIMIT)


@click.command()
@click.option('--file_of_paths',
    type=click.File('r'),
    default=FILE_PATH_OF_FILE_PATHS,
)
@click.option('--file_of_hashes',
    type=click.File('w'),
    default=FILE_PATH_OF_HASHES
)
def hashify(file_of_paths, file_of_hashes):
    click.echo("Reading the content at each path in the input file, hashing it, and dumping that hash to the output path...")
    read_and_hashify(input_file_of_filepaths=file_of_paths, output_file_of_hashes=file_of_hashes)


cli.add_command(import_photos)
cli.add_command(hashify)
