from hashlib import sha256


def read_and_hashify(input_file_of_filepaths, output_file_of_hashes):
    # if this is slow, i'll look into parallelizing it
    count_of_missing_files = 0
    count_of_proccessed_files = 0
    hashes = []
    for filepath in input_file_of_filepaths:
        readable_path = filepath.rstrip()
        try:
            image_contents = open(readable_path, 'rb').read()
        except FileNotFoundError:
            count_of_missing_files += 1
        else:
            hashes.append(sha256(image_contents).digest())
            count_of_proccessed_files += 1
    output_file_of_hashes.write(b"\n".join(hashes))
    return count_of_missing_files, count_of_proccessed_files