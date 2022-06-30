import unittest
from code import main
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 'Chrome/89.0.4389.72 Safari/537.36"}


class request_test(unittest.TestCase):
    def test_get_content_grequest(self):
        output = main.get_content_grequests(
            ("https://ru.dotabuff.com/heroes", "https://ru.dotabuff.com/heroes"))

        self.assertTrue(output[0].ok)
        self.assertTrue(output[1].ok)
        with self.assertRaises(requests.exceptions.MissingSchema):
            output = main.get_content_requests((0,))
        with self.assertRaises(requests.exceptions.MissingSchema):
            output = main.get_content_requests((3,))
        with self.assertRaises(requests.exceptions.MissingSchema):
            output = main.get_content_requests(("afeaf",))

            # output = main.get_content_grequests(
            #     ("https://pythonworld.ru/moduli/modul-unittest.html",
            #      "https://www.songsterr.com/a/wsa/guns-n-roses-sweet-child-o-mine-tab-s23",
            #      1,
            #      "afeaf",
            #      4))
            #
            # self.assertTrue(output[0].ok)
            # self.assertTrue(output[1].ok)
            # self.assertEquals(output[2], None)
            # self.assertEquals(output[3], None)
            # self.assertEquals(output[4], None)

    def test_get_content_requests(self):
        output = main.get_content_requests("https://ru.dotabuff.com/heroes")
        self.assertTrue(output.ok)
        output = main.get_content_requests("https://ru.dotabuff.com/herfoes")
        self.assertIsNone(output)
        with self.assertRaises(requests.exceptions.MissingSchema):
            output = main.get_content_requests(3)


if __name__ == '__main__':
    unittest.main()
