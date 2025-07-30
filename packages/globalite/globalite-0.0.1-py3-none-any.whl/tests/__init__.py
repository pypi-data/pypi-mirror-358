import os
import tempfile

class TempDirFixture:
    """ Sets up and tears down a temporary directory, within which the test will run.
    """
    
    def setUp(self):
        self._prev_directory_of_test = os.path.abspath(os.curdir)
        self._temporary_directory_of_test = tempfile.TemporaryDirectory()
        os.chdir(self._temporary_directory_of_test.name)

        super().setUp()

    def tearDown(self):
        self._temporary_directory_of_test.cleanup()
        os.chdir(self._prev_directory_of_test)

        super().tearDown()
