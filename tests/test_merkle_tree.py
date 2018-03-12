from io import BytesIO
from hashlib import sha256

import pytest

from app.merkle_tree import MerkleTree, MerkleProof


RAW_DATA_ELEMENTS = [b'in', b'west', b'philadelphia', b'born', b'and']
ACTUAL_FULL_TREE = [
    b'X)gSM\x0f\x90\x9d\x19k\x97\xf9\xe6\x92\x13Bwz\xea\x87\xb4o\xa5-\xf1e8\x9d\xb1\xfb\x8c\xcf',
    b'v\xa7\x96 \x8bqw\x9c\x031\xe7\x9e\x8a\xc1}\xf9y\xc7\xd2\xc5\xbd\x10\xb4\x91\xc9K\xd1\xe1mB \x88',
    b'[@br\xe9\x89\xb1\\\x0c\xc8!\xd3\x9fH\x9f\x1e#\x0ceW\xa3\xe0!k\x15kh\x10\x8dA\xfb(',
    b'\x08"\x967V\xcep\xec\x17\xb8\x9d\xf3?$\xe1\x19\x9b\xb7\x19\x9a.A\x81\x9f\xc3[GZ5\tv.',
    b'b\x01\x11\x1b\x83\xa0\xcb[\t"\xcb7\xccD+\x9a@\xe2N;\x1c\xe1\x00\xa4\xbb OLc\xfd*\xc0',
    b'\xc7\x1a\xb5\xf8\xa8\xd3\xaaTLf\x92\x0c\xa0J\x87\xba\x07z\x82qF\xd0\xaeY\xc3\x94"\xf0\xa5\xe4+W',
    b'Z5v\xc4k\xc9\xe5u\xcd\r$\xb4\xbb\x808>\xbaO\x12\x97\xef\x80\x14/L\xack\x19\xeb\x0c\xe0V',
    b' \xadYV\xf8e\x8b\xe4\x1f\x115\x9b\x92\xa7\x85\xf7\xcb\xe6\x15\xdbU\x01\x05\x99\x90y7G-D\xa2\xb6',
    b"\x9f7>\x00\xcf\x7f\x8f\x1c\xc1q\xe7#\xe8\xc1\xdcQ\x9cqI\xa8\xe8\xdcO\xc3\xd4\x89\xedm\xad`'\xc1",
    b'E\xd4x6q\x03\xdd\x16M\xa0i\xe5~\xdf\xd2-\xfa\xdb\x13\xebl\n\x01K\x80\xbd\x11\x1d\x12\x19Vm',
    b'\xac\xb9UIt\xe1\xa3\x9c\x83S;9\xd40\xedW\x91u\xf4ub*>D\x9c\xa7\x98\xbf\xa6\x87\xb4('
]


@pytest.fixture
def input_filestream_of_hashes():
    hashed_elements = [sha256(el).digest() for el in RAW_DATA_ELEMENTS]
    as_filestream = BytesIO(b'\n'.join(hashed_elements))
    return as_filestream


@pytest.fixture
def matching_filepath_builder(tmpdir):
    def inner(element_id):
        tempfile = tmpdir.join("matching.jpg")
        tempfile.write(RAW_DATA_ELEMENTS[element_id])
        return tempfile.realpath()
    return inner


@pytest.fixture
def unmatching_filepath(tmpdir):
    tempfile = tmpdir.join("unmatching.jpg")
    tempfile.write(b'youve never seen me before')
    return tempfile.realpath()


@pytest.fixture
def merkle_tree(input_filestream_of_hashes):
    return MerkleTree.from_filestream(input_filestream_of_hashes)


def verify_proof(proof):
    running_proof = proof.element_hash
    for element in proof.chain:
        if element[0] == 'left':
            to_hash = element[1] + running_proof
        elif element[0] == 'right':
            to_hash = running_proof + element[1]
        running_proof = sha256(to_hash).digest()
    return running_proof == proof.root


def test_root_is_correct(merkle_tree):
    expected_root = ACTUAL_FULL_TREE[-1]
    assert expected_root == merkle_tree.root


@pytest.mark.parametrize("element_id", range(len(RAW_DATA_ELEMENTS)))
def test_existence_true_for_all_element(merkle_tree, matching_filepath_builder, element_id):
    filepath = matching_filepath_builder(element_id)
    assert merkle_tree.test_existence(filepath) == True


def test_existence_false(merkle_tree, unmatching_filepath):
    assert merkle_tree.test_existence(unmatching_filepath) == False


def test_proof_nonexistent_element_is_false(merkle_tree, unmatching_filepath):
    actual_proof = merkle_tree.proof(unmatching_filepath)
    assert actual_proof == False


@pytest.mark.parametrize("element_id, path", [
    (0, [('right', 1), ('right', 6), ('right', 9)]),
    (1, [('left', 0),  ('right', 6), ('right', 9)]),
    (2, [('right', 3), ('left', 5), ('right', 9)]),
    (3, [('left', 2),  ('left', 5), ('right', 9)]),
    (4, [('right', 4), ('right', 7), ('left', 8)]),
])
def test_proof(element_id, path, merkle_tree, matching_filepath_builder):
    filepath = matching_filepath_builder(element_id)
    element_hash = sha256(open(filepath, 'rb').read()).digest()
    expected_chain = [ (step[0], ACTUAL_FULL_TREE[step[1]]) for step in path ]
    root = merkle_tree.root
    expected_proof = MerkleProof(element_hash, expected_chain, root)
    assert verify_proof(expected_proof) == True

    actual_proof = merkle_tree.proof(filepath)

    assert expected_proof == actual_proof
    assert verify_proof(actual_proof)
