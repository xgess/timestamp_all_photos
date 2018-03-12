from hashlib import sha256


def read_and_hashify(input_file_of_filepaths, output_file_of_hashes):
    # if this is slow, i'll look into parallelizing it
    hashes = []
    for filepath in input_file_of_filepaths:
        readable_path = filepath.rstrip()
        image_contents = open(readable_path, 'rb').read()
        hashes.append(sha256(image_contents).digest())
    output_file_of_hashes.write(b"\n".join(hashes))
