import os

import click

from .apple_photos_library import dump_image_paths
from .read_and_hashify import read_and_hashify
from .merkle_tree import MerkleTree, hash_from_path


TMP_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'tmp')
FILE_PATH_OF_FILE_PATHS = os.path.join(TMP_DIRECTORY, 'file_paths_to_hashify.txt')
FILE_PATH_OF_HASHES = os.path.join(TMP_DIRECTORY, 'hashes.dat')
LIMIT = 5000


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
    type=click.File('wb'),
    default=FILE_PATH_OF_HASHES
)
def hashify(file_of_paths, file_of_hashes):
    click.echo("Reading the content at each path in the input file, hashing it, and dumping that hash to the output path...")
    read_and_hashify(input_file_of_filepaths=file_of_paths, output_file_of_hashes=file_of_hashes)


@click.command()
@click.option('--file_of_hashes',
    type=click.File('rb'),
    default=FILE_PATH_OF_HASHES
)
def build_merkle(file_of_hashes):
    click.echo("Read all of the hashes into a data structure...")
    tree = MerkleTree.from_filestream(file_of_hashes)
    click.echo(f"root of the tree: {tree.root}")
    definitely_in_path = '/Users/me/Pictures/Photos Library.photoslibrary/Masters/2017/08/26/20170826-150604/IMG_0988.JPG'
    item_hash = hash_from_path(definitely_in_path)
    click.echo(f"item hash: {item_hash}")
    is_in = tree.test_existence(definitely_in_path)
    click.echo(f"expected true: {is_in}")
    evidence = tree.proof(definitely_in_path)
    click.echo(f"evidence: {evidence}")


@click.command()
@click.pass_context
def end_to_end(context):
    context.invoke(import_photos)
    context.invoke(hashify)
    context.invoke(build_merkle)


cli.add_command(end_to_end)
cli.add_command(import_photos)
cli.add_command(hashify)
cli.add_command(build_merkle)
