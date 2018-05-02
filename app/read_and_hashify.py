import concurrent.futures
from hashlib import sha256


def read_and_hashify(input_file_of_filepaths, output_file_of_hashes):
    image_paths = [fp.rstrip() for fp in input_file_of_filepaths]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        parallel_results = executor.map(hash_from_filepath, image_paths)

    image_hashes = [ih for ih in parallel_results if ih is not None]
    count_of_proccessed_files = len(image_hashes)
    count_of_missing_files = len(parallel_results) - count_of_proccessed_files

    output_file_of_hashes.write(b"\n".join(image_hash))

    return count_of_missing_files, count_of_proccessed_files


def hash_from_filepath(filepath):
    try:
        image_contents = open(filepath, 'rb').read()
    except FileNotFoundError:
        return None
    else:
        return sha256(image_contents).digest()
