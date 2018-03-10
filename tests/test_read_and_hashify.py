import io
import os

from app.read_and_hashify import read_and_hashify


TEST_DIRECTORY = os.path.dirname(__file__)
MOCK_LIBRARY_PATH = os.path.join(TEST_DIRECTORY, 'fixtures', 'Mock Photos Library')
TEST_PHOTO_PATH = os.path.join(MOCK_LIBRARY_PATH, 'Masters', 'arbitrary_nesting', 'test.jpg')
HASH_OF_PHOTO = 'ad8d235654b062dfdceb7fbe5c02dcaab0acf87373d773d20375ad9ac6955b95'


def test_read_and_hashify():
    input_stream = io.StringIO(TEST_PHOTO_PATH + '\n')
    output_stream = io.StringIO()
    expected_stream_contents = HASH_OF_PHOTO

    read_and_hashify(input_stream, output_stream)
    actual_stream_contents = output_stream.getvalue()

    assert actual_stream_contents == expected_stream_contents
