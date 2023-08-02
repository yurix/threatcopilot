import src.home.util as util

class TestUtil:
    def test_safe_is_empty_list(self):
            testdata = list()
            assert util.safe_is_empty_list(testdata)

    def test_safe_is_empty_list_none(self):
            testdata = None
            assert util.safe_is_empty_list(testdata)

    def test_safe_is_empty_list_wrong_type(self):
            testdata = []
            assert util.safe_is_empty_list(testdata)

    def test_safe_is_empty_list_not_empty(self):
            testdata = list("hello")
            assert not util.safe_is_empty_list(testdata)
    
    def test_safe_is_not_empty_list(self):
            testdata = list()
            assert not util.safe_is_not_empty_list(testdata)

    def test_safe_is_not_empty_list_none(self):
            testdata = None
            assert not util.safe_is_not_empty_list(testdata)

    def test_safe_is_not_empty_list_wrong_type(self):
            testdata = []
            assert not util.safe_is_not_empty_list(testdata)

    def test_safe_is_not_empty_list_not_empty(self):
            testdata = list("hello")
            assert util.safe_is_not_empty_list(testdata)