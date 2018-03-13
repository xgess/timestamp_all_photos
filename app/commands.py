from hashlib import sha256
import os
import random
import subprocess

import click

from .apple_photos_library import dump_image_paths
from .merkle_tree import MerkleTree, hash_from_path
from .read_and_hashify import read_and_hashify
from .transmit import send_to_bitcoin


TMP_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'tmp')
FILE_PATH_OF_FILE_PATHS = os.path.join(TMP_DIRECTORY, 'file_paths_to_hashify.txt')
FILE_PATH_OF_HASHES = os.path.join(TMP_DIRECTORY, 'hashes.dat')
CURRENT_USERNAME = subprocess.check_output(['whoami']).decode().rstrip()
DEFAULT_LIBRARY_PATH = f'/Users/{CURRENT_USERNAME}/Pictures/Photos Library.photoslibrary/'
LIMIT = 500


_transmission_options = [
    click.option('--wif', prompt=True, hide_input=True, help='private key in wallet-input-format'),
    click.option('--change_address', default=None, help='defaults to the address you sent from'),
    click.option('--mainnet', 'is_testnet', flag_value=False),
    click.option('--testnet', 'is_testnet', flag_value=True, default=True),
    click.option('--live', 'is_dryrun', flag_value=False),
    click.option('--dryrun', 'is_dryrun', flag_value=True, default=True),
]

def transmission_options(func):
    for option in reversed(_transmission_options):
        func = option(func)
    return func


@click.group()
def cli():
    pass


@click.command()
@click.option('--library',
    type=click.Path(exists=True),
    default=DEFAULT_LIBRARY_PATH,
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
    count_of_missing_files, count_of_proccessed_files = read_and_hashify(input_file_of_filepaths=file_of_paths, output_file_of_hashes=file_of_hashes)
    click.echo(f"processed: {count_of_proccessed_files}, couldn't find: {count_of_missing_files}")



def lookup_random_photo_filepath(ctx, param, value):
    if value is None:
        all_paths = open(FILE_PATH_OF_FILE_PATHS).read().splitlines()
        return random.choice(all_paths)

@click.command()
@click.option('--file_of_hashes',
    type=click.File('rb'),
    default=FILE_PATH_OF_HASHES
)
@click.option('--expected_included_filepath', callback=lookup_random_photo_filepath)
def build_and_verify_merkle(file_of_hashes, expected_included_filepath):
    click.echo("Read all of the hashes into a data structure...")
    tree = MerkleTree.from_filestream(file_of_hashes)
    click.echo(f"   root of the tree: {tree.root}")
    click.echo(f"Verifying merkle tree...")
    click.echo(f"   looking for path: {expected_included_filepath}")
    item_hash = hash_from_path(expected_included_filepath)
    click.echo(f"   item hash to verify: {item_hash}")
    is_in = tree.test_existence(expected_included_filepath)
    click.echo(f"   it exists in the tree: {is_in}")
    evidence = tree.proof(expected_included_filepath)
    click.echo(f"   proof object: {evidence}")
    click.echo(f"Verifying evidence...")

    running_proof = evidence.element_hash
    click.echo(f"   running_hash: {running_proof}")
    for element in evidence.chain:
        if element[0] == 'left':
            to_hash = element[1] + running_proof
        elif element[0] == 'right':
            to_hash = running_proof + element[1]
        running_proof = sha256(to_hash).digest()
        click.echo(f"   running_hash: {running_proof}")
    is_verified = (running_proof == tree.root)
    click.echo(f"   does running_hash == merkle_root ??")
    click.echo(f"{'Everything looks good' if is_verified else '*** Something is wrong ***'}")
    assert is_verified


@click.command()
@transmission_options
@click.option('--file_of_hashes',
    type=click.File('rb'),
    default=FILE_PATH_OF_HASHES
)
def send_merkle_root_to_bitcoin(file_of_hashes, wif, change_address, is_testnet, is_dryrun):
    click.echo("Calculating merkle root...")
    tree = MerkleTree.from_filestream(file_of_hashes)
    click.echo(f"   merkle root: {tree.root}")
    payload = tree.root
    click.echo(f"Sending to Bitcoin...")
    transaction = send_to_bitcoin(wif, change_address, payload, is_testnet, is_dryrun)
    click.echo(f"   transaction: {transaction}")


@click.command()
@transmission_options
@click.option('--library',
    type=click.Path(exists=True),
    default=DEFAULT_LIBRARY_PATH,
    help='path to photos library object'
)
@click.pass_context
def end_to_end(context, library, **transmission_options):
    context.invoke(import_photos, library=library)
    context.invoke(hashify)
    context.invoke(send_merkle_root_to_bitcoin, **transmission_options)


cli.add_command(end_to_end)
cli.add_command(import_photos)
cli.add_command(hashify)
cli.add_command(build_and_verify_merkle)
cli.add_command(send_merkle_root_to_bitcoin)
