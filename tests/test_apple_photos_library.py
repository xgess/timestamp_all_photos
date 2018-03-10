import os

from app.apple_photos_library import dump_image_paths


TEST_DIRECTORY = os.path.dirname(__file__)
MOCK_LIBRARY_PATH = os.path.join(TEST_DIRECTORY, 'fixtures', 'Mock Photos Library')
DESTINATION_PATH = os.path.join(TEST_DIRECTORY, 'tmp', 'test_image_paths.txt')


class Test:

    def setup_method(self, test_method):
        assert not os.path.exists(DESTINATION_PATH)

    def teardown_method(self, test_method):
        os.remove(DESTINATION_PATH)

    def test_dump_image_paths(self):
        dump_image_paths(MOCK_LIBRARY_PATH, DESTINATION_PATH)

        expected_file_contents = TEST_DIRECTORY + '/fixtures/Mock\ Photos\ Library/Masters/arbitrary_nesting/test.jpg\n'
        actual_file_contents = open(DESTINATION_PATH).read()
        assert expected_file_contents == actual_file_contents


# to recreate the fake database in ipython
    # import sqlite3
    # conn = sqlite3.connect('photos.db')
    # cur = conn.cursor()
    # cur.execute("create table RKMaster (imagePath text)")
    # cur.execute("""insert into RKMaster values ('arbitrary_nesting/test.jpg')""")
    # conn.commit()
