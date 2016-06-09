#!/usr/bin/python

import chandere.core
import re
import time
import threading
import queue
import unittest

class CoreTest(unittest.TestCase):
    def test_generate_urls(self):
        self.assertEqual(
            list(chandere.core.generate_urls(
                chan="4chan",
                board="/g/"
            )),
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
            list(chandere.core.generate_urls(
                chan="4chan",
                board="/g/",
                bottomfeed=True
            )),
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
            list(chandere.core.generate_urls(
                chan="4chan",
                board="/g/",
                ssl=True
            )),
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
            next(chandere.core.generate_urls(
                chan="4chan",
                board="/g/",
                thread="51971506"
            )),
            "http://boards.4chan.org/g/thread/51971506"
        )

    def test_create_offsets(self):
        self.assertEqual(
            chandere.core.create_offsets("ar", "lainchan"),
            {
            "max_page": 7,
            "page_delimiter": "",
            "thread_delimiter": "res/",
            "board_initial": re.compile(r'(?<=header><h1>)\S+?'),
            "post_op": re.compile(r'(?<=post op").+?(?=<\/div>)'),
            "post_reply":
            re.compile(r'(?<=post reply">).+?(?=<\/div><\/div>)'),
            "post_id": re.compile(r'(?<=<a id=")\d+(?=" class="post_anchor")'),
            "file_name": re.compile(r'(?<=\/)\d+?\.\w{3,4}'),
            "poster_name": re.compile(r'(?<=class="name">).*?(?=</span>)'),
            "post_title": re.compile(r'(?<=class="subject">).*?(?=</span>)'),
            "pub_date": re.compile(r'\d{4}-\d{2}-\d{2}'),
            "pub_time": re.compile(r'\d{2}:\d{2}:\d{2}'),
            "post_body": re.compile(r'(?<=class="body">).+?(?=<\/div)')
        }
        )
        self.assertEqual(
            chandere.core.create_offsets("id", "lainchan"),
            {
            "max_page": 7,
            "page_delimiter": "",
            "thread_delimiter": "res/",
            "link_prefix": "https://lainchan.org",
            "board_initial": re.compile(r'(?<=header><h1>)\S+?'),
            "post_op": re.compile(r'(?<=post op").+?(?=<\/div>)'),
            "post_reply":
            re.compile(r'(?<=post reply">).+?(?=<\/div><\/div>)'),
            "thread_link":
            re.compile(r'(?<=<div id="op_)\d+(?=" class="post op")'),
            "image_link": re.compile(r'((?<=File: <a href=")|(?<=" href=")).+?\.\w{3,4}(?=")'),
            "file_name": re.compile(r'(?<=\/)\d+?\.\w{3,4}')
        }
        )
        self.assertEqual(
            chandere.core.create_offsets("ar", "4chan"),
            {
            "max_page": 10,
            "page_delimiter": "",
            "thread_delimiter": "thread/",
            "board_initial": re.compile(r'(?<=boardTitle">)\/\S+?\/'),
            "post_op":
            re.compile(r'(?<=post op">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_reply":
            re.compile(r'(?<=post reply">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_id": re.compile(r'(?<=#p)\d+(?=")'),
            "file_name": re.compile(r'(?<=target="_blank">).+?\.\w{3,4}(?=</a>)'),
            "poster_name": re.compile(r'(?<=class="name">).*?(?=</span>)'),
            "post_title": re.compile(r'(?<=class="subject">).*?(?=</span>)'),
            "pub_date": re.compile(r'\d{2}\/\d{2}\/\d{2}\(\w{3}\)'),
            "pub_time": re.compile(r'\d{2}:\d{2}:\d{2}'),
            "post_body":
            re.compile(r'(?<="postMessage" id="m\d{8}">).+?(?=<\/block)')
        }
        )
        self.assertEqual(
            chandere.core.create_offsets("id", "4chan"),
            {
            "max_page": 10,
            "page_delimiter": "",
            "thread_delimiter": "thread/",
            "link_prefix": "http:",
            "board_initial": re.compile(r'(?<=boardTitle">)\/\S+?\/'),
            "post_op":
            re.compile(r'(?<=post op">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_reply":
            re.compile(r'(?<=post reply">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_id": re.compile(r'(?<=#p)\d+(?=")'),
            "image_link": re.compile(r'((?<=File: <a href=")|(?<=" href=")).+?\.\w{3,4}(?=")'),
            "file_name":
            re.compile(r'(?<=target="_blank">).+?\.\w{3,4}(?=</a>)')
        }
        )
        self.assertEqual(
            chandere.core.create_offsets("ar", "nullxnull"),
            {
            "max_page": None,
            "page_delimiter": "",
            "thread_delimiter": "thread/",
            "board_initial": re.compile(r'(?<=boardTitle">)\/\S+?\/'),
            "post_op":
            re.compile(r'(?<=post op">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_reply":
            re.compile(r'(?<=post reply">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_id": re.compile(r'(?<=#p)\d+(?=")'),
            "file_name": re.compile(r'(?<=target="_blank">).+?\.\w{3,4}(?=</a>)'),
            "poster_name": re.compile(r'(?<=class="name">).*?(?=</span>)'),
            "post_title": re.compile(r'(?<=class="subject">).*?(?=</span>)'),
            "pub_date": re.compile(r'\d{2}\/\d{2}\/\d{2}\(\w{3}\)'),
            "pub_time": re.compile(r'\d{2}:\d{2}:\d{2}'),
            "post_body":
            re.compile(r'(?<="postMessage" id="m\d{8}">).+?(?=<\/block)')
        }
        )
        self.assertEqual(
            chandere.core.create_offsets("id", "nullxnull"),
            {
            "max_page": None,
            "page_delimiter": "",
            "thread_delimiter": "thread/",
            "link_prefix": "http:",
            "board_initial": re.compile(r'(?<=boardTitle">)\/\S+?\/'),
            "post_op":
            re.compile(r'(?<=post op">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_reply":
            re.compile(r'(?<=post reply">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_id": re.compile(r'(?<=#p)\d+(?=")'),
            "image_link": re.compile(r'((?<=File: <a href=")|(?<=" href=")).+?\.\w{3,4}(?=")'),
            "file_name":
            re.compile(r'(?<=target="_blank">).+?\.\w{3,4}(?=</a>)')
        }
        )

if __name__ == "__main__":
    unittest.main()
