import math
from hashlib import sha256
from typing import NamedTuple, List, Union, Tuple


class Sibling(NamedTuple):
    direction: str
    idx: int  # mypy doesn't like attributes called `index`


class ProofChainElement(NamedTuple):
    direction: str
    node_hash: bytes


class MerkleProof(NamedTuple):
    element_hash: bytes
    chain: List[ProofChainElement]
    root: bytes


def hash(something: bytes) -> bytes:
    return sha256(something).digest()


def hash_from_path(file_path) -> bytes:
    file_contents = open(file_path, 'rb').read()
    return hash(file_contents)


def _build_simple_merkle_tree_list(items: List[bytes]) -> List[bytes]:
    # shamelessly inspired by https://github.com/petertodd/python-bitcoinlib/
    data_structure = list(items)

    generation_size = len(items)
    generation_start_index = 0
    while generation_size > 1:
        for left_offset in range(0, generation_size, 2):
            right_offset = min(left_offset + 1, generation_size - 1)
            left_element = data_structure[generation_start_index + left_offset]
            right_element = data_structure[generation_start_index + right_offset]
            data_structure.append(hash(left_element + right_element))

        generation_start_index += generation_size
        generation_size = (generation_size + 1) // 2

    return data_structure


class MerkleTree:

    def __init__(self, items: List[bytes]) -> None:
        self.data = _build_simple_merkle_tree_list(items)
        self.size = len(items)
        self.height = len(self.data).bit_length()
        self.root = self.data[-1]


    @classmethod
    def from_filestream(cls, input_filestream):
        file_contents = input_filestream.readlines()
        items = [pic_hash.rstrip() for pic_hash in file_contents]
        return cls(items)


    def test_existence(self, file_path) -> bool:
        return self._is_hashed_element_present(hash_from_path(file_path))


    def _is_hashed_element_present(self, hashed_element: bytes):
        return hashed_element in self.data[:self.size]


    def _generation_bounds_for_index(self, index) -> Tuple[int, int]:
        gen_start, gen_end = (0, self.size - 1)
        for _ in range(self.height - 2):
            if (gen_start <= index <= gen_end):
                break
            current_gen_size = gen_end - gen_start + 1
            gen_start = gen_end + 1
            gen_end = math.ceil(current_gen_size / 2) + gen_start - 1
        return gen_start, gen_end


    def _sibling(self, index: int) -> Union[None, Sibling]:
        if index == len(self.data) - 1:
            # the root element has no siblings
            return None
        gen_start, gen_end = self._generation_bounds_for_index(index)

        if (index - gen_start) % 2 == 0:
            if index == gen_end:
                # item is its own sibling
                return Sibling('right', index)
            else:
                return Sibling('right', index + 1)
        else:
            return Sibling('left', index - 1)


    def _parent(self, index) -> Union[None, int]:
        if index == len(self.data) - 1:
            # the root element has no parent
            return None
        gen_start, gen_end = self._generation_bounds_for_index(index)
        return (index - gen_start) // 2 + gen_end + 1


    def proof(self, file_path) -> Union[MerkleProof, bool]:
        element_hash = hash_from_path(file_path)
        try:
            element_index = self.data.index(element_hash)
        except ValueError:
            # element not in tree
            return False

        # the proof chain is each element's parent's sibling
        # so walk that up to the root
        chain = []
        next_element = self._sibling(element_index)
        while next_element is not None:
            proof_chain_element = ProofChainElement(next_element.direction, self.data[next_element.idx])
            chain.append(proof_chain_element)
            next_element = self._sibling(self._parent(next_element.idx))

        return MerkleProof(element_hash, chain, self.root)
