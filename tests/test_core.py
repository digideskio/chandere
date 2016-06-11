#!/usr/bin/python

try:
    import queue
except ImportError:
    import Queue as queue
import os
import re
import time
import pickle
import threading
import unittest

import chandere.core


class UrlGeneratorTest(unittest.TestCase):
    def test_generate_board_urls(self):
        self.assertEqual(
            list(chandere.core.generate_urls("4chan", "/g/")),
            ["http://boards.4chan.org/g/",
             "http://boards.4chan.org/g/2",
             "http://boards.4chan.org/g/3",
             "http://boards.4chan.org/g/4",
             "http://boards.4chan.org/g/5",
             "http://boards.4chan.org/g/6",
             "http://boards.4chan.org/g/7",
             "http://boards.4chan.org/g/8",
             "http://boards.4chan.org/g/9",
             "http://boards.4chan.org/g/10"
            ]
        )
        self.assertEqual(
            list(chandere.core.generate_urls("4chan", "/c/")),
            ['http://boards.4chan.org/c/',
             'http://boards.4chan.org/c/2',
             'http://boards.4chan.org/c/3',
             'http://boards.4chan.org/c/4',
             'http://boards.4chan.org/c/5',
             'http://boards.4chan.org/c/6',
             'http://boards.4chan.org/c/7',
             'http://boards.4chan.org/c/8',
             'http://boards.4chan.org/c/9',
             'http://boards.4chan.org/c/10'
            ]
        )
        self.assertEqual(
            list(chandere.core.generate_urls("lainchan", "/cyb/")),
            ['http://lainchan.org/cyb/',
             'http://lainchan.org/cyb/2',
             'http://lainchan.org/cyb/3',
             'http://lainchan.org/cyb/4',
             'http://lainchan.org/cyb/5',
             'http://lainchan.org/cyb/6',
             'http://lainchan.org/cyb/7',
             'http://lainchan.org/cyb/8',
             'http://lainchan.org/cyb/9',
             'http://lainchan.org/cyb/10'
            ]
        )
        
    def test_bottomfeed_mode(self):
        self.assertEqual(
            list(chandere.core.generate_urls("4chan", "/g/", bottomfeed=True)),
            ["http://boards.4chan.org/g/10",
             "http://boards.4chan.org/g/9",
             "http://boards.4chan.org/g/8",
             "http://boards.4chan.org/g/7",
             "http://boards.4chan.org/g/6",
             "http://boards.4chan.org/g/5",
             "http://boards.4chan.org/g/4",
             "http://boards.4chan.org/g/3",
             "http://boards.4chan.org/g/2",
             "http://boards.4chan.org/g/"
            ]
        )
        self.assertEqual(
            list(chandere.core.generate_urls("lainchan", "/cyb/",
                                             bottomfeed=True)),
            ['http://lainchan.org/cyb/10',
             'http://lainchan.org/cyb/9',
             'http://lainchan.org/cyb/8',
             'http://lainchan.org/cyb/7',
             'http://lainchan.org/cyb/6',
             'http://lainchan.org/cyb/5',
             'http://lainchan.org/cyb/4',
             'http://lainchan.org/cyb/3',
             'http://lainchan.org/cyb/2',
             'http://lainchan.org/cyb/'
            ]
        )
        
    def test_force_ssl_mode(self):
        self.assertEqual(
            list(chandere.core.generate_urls("4chan", "/g/", ssl=True)),
            ["https://boards.4chan.org/g/",
             "https://boards.4chan.org/g/2",
             "https://boards.4chan.org/g/3",
             "https://boards.4chan.org/g/4",
             "https://boards.4chan.org/g/5",
             "https://boards.4chan.org/g/6",
             "https://boards.4chan.org/g/7",
             "https://boards.4chan.org/g/8",
             "https://boards.4chan.org/g/9",
             "https://boards.4chan.org/g/10"
            ]
        )
        self.assertEqual(
            list(chandere.core.generate_urls("lainchan", "/cyb/", ssl=True)),
            ['https://lainchan.org/cyb/',
             'https://lainchan.org/cyb/2',
             'https://lainchan.org/cyb/3',
             'https://lainchan.org/cyb/4',
             'https://lainchan.org/cyb/5',
             'https://lainchan.org/cyb/6',
             'https://lainchan.org/cyb/7',
             'https://lainchan.org/cyb/8',
             'https://lainchan.org/cyb/9',
             'https://lainchan.org/cyb/10'
            ]
        )
        
    def test_thread_mode(self):
        self.assertEqual(
            next(chandere.core.generate_urls("4chan", "/g/", "51971506")),
            "http://boards.4chan.org/g/thread/51971506"
        )
        self.assertEqual(
            next(chandere.core.generate_urls("lainchan", "/cyb/", "26278")),
            "http://lainchan.org/cyb/thread/26278"
        )

    def test_delimiters(self):
        self.assertEqual(
            list(chandere.core.generate_urls("lainchan", "/cyb/",
                                             page_delimiter="page/")),
            ['http://lainchan.org/cyb/',
             'http://lainchan.org/cyb/page/2',
             'http://lainchan.org/cyb/page/3',
             'http://lainchan.org/cyb/page/4',
             'http://lainchan.org/cyb/page/5',
             'http://lainchan.org/cyb/page/6',
             'http://lainchan.org/cyb/page/7',
             'http://lainchan.org/cyb/page/8',
             'http://lainchan.org/cyb/page/9',
             'http://lainchan.org/cyb/page/10'
            ]
        )
        self.assertEqual(
            next(chandere.core.generate_urls("lainchan", "/cyb/", "26278",
                                             thread_delimiter="res/")),
            "http://lainchan.org/cyb/res/26278"
        )

    def test_max_page(self):
        self.assertEqual(
            list(chandere.core.generate_urls("4chan", "/f/", max_page=1)),
            ['http://boards.4chan.org/f/']
        )
        self.assertEqual(
            list(chandere.core.generate_urls("lainchan", "/cyb/", max_page=7)),
            ['http://lainchan.org/cyb/',
             'http://lainchan.org/cyb/2',
             'http://lainchan.org/cyb/3',
             'http://lainchan.org/cyb/4',
             'http://lainchan.org/cyb/5',
             'http://lainchan.org/cyb/6',
             'http://lainchan.org/cyb/7'
            ]
        )


class OffsetsTest(unittest.TestCase):
    def test_create_offsets(self):
        self.assertTrue(chandere.core.create_offsets("id", "4chan"))
        self.assertTrue(chandere.core.create_offsets("id", "lainchan"))
        self.assertTrue(chandere.core.create_offsets("id"))
        self.assertTrue(chandere.core.create_offsets("ar", "4chan"))
        self.assertTrue(chandere.core.create_offsets("ar", "lainchan"))
        self.assertTrue(chandere.core.create_offsets("ar"))
        self.assertTrue(chandere.core.create_offsets("tc", "4chan"))
        self.assertTrue(chandere.core.create_offsets("tc", "lainchan"))
        self.assertTrue(chandere.core.create_offsets("tc"))


# class ConnectionThreadTest(unittest.TestCase):
#     def setUp(self):
#         self.cache = []
#         self.url_queue = queue.Queue()
#         self.html_queue = queue.Queue()
        
#     def test_successful_connection(self):
#         self.url_queue.put("http://boards.4chan.org/g/")
#         chandere.core.get_url_content(self.url_queue, self.html_queue,
#                                       self.cache, debug=True)
#         self.assertTrue(self.html_queue.get())

#     def test_404_connection(self):
#         self.url_queue.put("http://boards.4chan.org/z/")
#         chandere.core.get_url_content(self.url_queue, self.html_queue,
#                                       self.cache, debug=True)
#         self.assertTrue(self.html_queue.empty())

#     def test_blocked_connection(self):
#         self.url_queue.put("https://8ch.net/tech/index.html")
#         chandere.core.get_url_content(self.url_queue, self.html_queue,
#                                       self.cache, debug=True)
#         self.assertTrue(self.html_queue.empty())

#     def test_cache_removal(self):
#         self.url_queue.put("http://boards.4chan.org/z/")
#         self.cache.append(("/z/", None, "4chan", "http://boards.4chan.org/z/"))
#         chandere.core.get_url_content(self.url_queue, self.html_queue,
#                                       self.cache, debug=True)
#         self.assertTrue(len(self.cache) == 0)


class ScraperThreadTest(unittest.TestCase):
    def setUp(self):
        self.cache = []
        self.html_queue = queue.Queue()
        self.data_queue = queue.Queue()

    def test_find_images(self):
        offsets = chandere.core.create_offsets("id", "4chan")
        with open("tests/example_page") as page:
            self.html_queue.put(page.read())
        chandere.core.scrape_html(offsets, "id", "4chan", self.html_queue,
                                  self.data_queue, self.cache, debug=True)
        info = self.data_queue.get()
        self.assertEqual(info, ("http://i.4cdn.org/g/1465635673193.jpg",
                                "back.jpg"))

    def test_archive_posts(self):
        offsets = chandere.core.create_offsets("ar", "4chan")
        with open("tests/example_page") as page:
            self.html_queue.put(page.read())
        chandere.core.scrape_html(offsets, "ar", "4chan", self.html_queue,
                                  self.data_queue, self.cache, debug=True)
        info = self.data_queue.get()
        self.assertEqual(info, ("55021750", None, "Anonymous", "06/11/16(Sat)",
                                "05:01:13", "back.jpg", "",
                                "Best .cbr reader for android?"))


class WriteThreadTest(unittest.TestCase):
    def setUp(self):
        self.data_queue = queue.Queue()

    # def test_download_image(self):
    #     self.data_queue.put(("http://i.4cdn.org/g/1450659832892.png",
    #                          "test.png"))
    #     chandere.core.write_to_disk("id", ".", None, self.data_queue,
    #                                 debug=True)
    #     self.assertTrue(os.path.exists("test.png"))
    #     os.remove("test.png")

    def test_archive_post(self):
        self.data_queue.put(("51971506", None, "Anonymous", "12/20/15(Sun)",
                             "20:03:52", "RMS.png", "", "Sticky"))
        chandere.core.write_to_disk("ar", "./archive.txt", "w+",
                                    self.data_queue, debug=True)
        self.assertTrue(os.path.exists("archive.txt"))
        with open("archive.txt") as archive:
            self.assertEqual(archive.read(), "\n********************\nPost ID:"
                              " 51971506\nFile: RMS.png\nAnonymous posted this "
                              "on 12/20/15(Sun) at 20:03:52\nSticky"
                              "\n********************")
        os.remove("archive.txt")


class CacheLoadTest(unittest.TestCase):
    def setUp(self):
        cache = ["id", ("/g/", "55021750", "4chan",
                        "http://boards.4chan.org/g/thread/51971506")]
        with open("test_cache.txt", "wb+") as cache_file:
            pickle.dump(cache, cache_file)

    def test_successful_cache_load(self):
        loaded_cache = chandere.core.load_cache("id", "./test_cache.txt")
        self.assertTrue(len(loaded_cache) != 0)

    def test_unsuccessful_cache_load(self):
        loaded_cache = chandere.core.load_cache("ar", "./test_cache.txt")
        self.assertTrue(len(loaded_cache) == 0)

    def tearDown(self):
        os.remove("test_cache.txt")


if __name__ == "__main__":
    unittest.main()
