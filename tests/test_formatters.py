#!/usr/bin/python

from chandere.formatters import separate_board_thread, parse_path
import os
import unittest


class FormattersTest(unittest.TestCase):
    def setUp(self):
        open("test_file.txt", "w+").close()
        
    def tearDown(self):
        os.remove("test_file.txt")
        
    def test_separate_board_thread(self):
        self.assertEqual(separate_board_thread(["/g/"]), [('/g/', None)])
        self.assertEqual(separate_board_thread(["g/"]), [('/g/', None)])
        self.assertEqual(separate_board_thread(["/g"]), [('/g/', None)])
        self.assertEqual(separate_board_thread(["g"]), [('/g/', None)])
        self.assertEqual(
            separate_board_thread(["/g/1234567890"]), [('/g/', '1234567890')])
        self.assertEqual(
            separate_board_thread(["g/1234567890"]), [('/g/', '1234567890')])
        self.assertEqual(
            separate_board_thread(["/g/ 1234567890"]), [('/g/', '1234567890')])
        self.assertEqual(
            separate_board_thread(["g/ 1234567890"]), [('/g/', '1234567890')])
        self.assertEqual(
            separate_board_thread(["/g 1234567890"]), [('/g/', '1234567890')])
        self.assertEqual(
            separate_board_thread(["g 1234567890"]), [('/g/', '1234567890')])
        self.assertEqual(separate_board_thread(["/g/", "/3/"]), [('/g/', None), ('/3/', None)])

    def test_parse_directory_file(self):
        self.assertEqual(parse_path(".", "id"), (".", None))
        self.assertEqual(parse_path("./test_dir", "id"), ("./test_dir", None
                                                           ))
        self.assertTrue(os.path.exists("./test_dir") and
                        os.path.isdir("./test_dir"))
        # Should be in tearDown, but doesn't work there for some reason.
        os.rmdir("./test_dir")
        #self.assertRaises(SystemExit, parse_path("./test_dir.txt", "id"))
        #self.assertRaises(SystemExit, parse_path("./n0p3/inexitant", "id"))
        self.assertEqual(
            parse_path("./test_file.txt", "ar"), ("./test_file.txt", "a"))
        self.assertEqual(
            parse_path("./inexistent_file.txt", "ar"),
            ("./inexistent_file.txt", "a+"))
        self.assertEqual(
            parse_path("./tests", "ar"), ("./tests/archive.txt", "a+"))



if __name__ == "__main__":
    unittest.main()
