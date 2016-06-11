"""Core module for Chandere, containing everything required to scrape a given
imageboard.
"""

try:
    import queue
    from urllib.request import urlopen, urlretrieve
    from urllib.error import HTTPError
except ImportError:
    import Queue as queue
    from urllib import urlopen, urlretrieve
from contextlib import closing
import re
import os
import pickle
import threading
import logging
import time

AVAILABLE_MODES = ["tc", "id", "ar"]
KNOWN_CHANS = {"4chan": "boards.4chan.org", "lainchan": "lainchan.org"}


def generate_urls(chan,
                  board,
                  thread=None,
                  ssl=False,
                  bottomfeed=False,
                  thread_delimiter="thread/",
                  page_delimiter="",
                  max_page=10):
    """Generator that yields URLs for all of a  board's pages if a thread is
    not specified. Otherwise, yields the URL for the specified thread.
    """
    prefix = "https://" if ssl else "http://"
    max_page = 26 if max_page is None else max_page + 1
    if chan in KNOWN_CHANS:
        base_url = prefix + KNOWN_CHANS[chan] + board
    else:
        try:
            base_url = prefix + re.search(r'[\d\w]+\.\S{2,}',
                                          chan).group() + board
        except AttributeError:
            logging.critical("Invalid URL, \"%s\"." % chan)
            exit(1)
    if thread:
        yield base_url + thread_delimiter + thread
    else:
        for page in range(
                1,
                max_page) if not bottomfeed else reversed(range(1, max_page)):
            if page == 1:
                yield base_url
            else:
                yield base_url + page_delimiter + str(page)


def get_url_content(url_queue, html_queue, cache, debug=False):
    """Thread to handle connections to the imageboard being scraped from."""
    logging.info("Starting...")
    while True:
        url = url_queue.get()
        try:
            with closing(urlopen(url)) as page:
                raw_html = page.read().decode()
            page_title = re.search(r"(?<=<title>).+?(?=</title>)",
                                   raw_html).group()
            if "404" in page_title:
                logging.critical("Inexistent page \"%s\"." % url)
                # The following is repeated four times. Should be refactored.
                if url in [post[3] for post in cache]:
                    for index, post in enumerate(cache):
                        if post[3] == url:
                            logging.warning("Removing url from cache.")
                            del cache[index]
            elif "access denied" in page_title.lower():
                logging.critical("Servers are blocking web scrapers.")
                if url in [post[3] for post in cache]:
                    for index, post in enumerate(cache):
                        if post[3] == url:
                            logging.warning("Removing url from cache.")
                            del cache[index]
            else:
                html_queue.put(raw_html)
                logging.info("Page, \"%s\", loaded." % page_title)
        except HTTPError as httpstatus:
            if str(httpstatus) == "HTTP Error 404: Not Found":
                logging.critical("Inexistent page \"%s\"." % url)
                if url in [post[3] for post in cache]:
                    for index, post in enumerate(cache):
                        if post[3] == url:
                            logging.warning("Removing url from cache.")
                            del cache[index]
            elif str(httpstatus) == "HTTP Error 403: Forbidden":
                logging.critical("Servers are blocking web scrapers.")
                if url in [post[3] for post in cache]:
                    for index, post in enumerate(cache):
                        if post[3] == url:
                            logging.warning("Removing url from cache.")
                            del cache[index]
        if debug:
            break


def scrape_html(offsets, mode, chan, html_queue, data_queue, cache, ssl=False,
                thread_delimiter="thread/", debug=False):
    logging.info("Starting...")
    while True:
        html = html_queue.get()
        board = re.search(offsets["board_initial"], html).group()
        thread_mode = bool(re.search(r'Return</a>', html))
        for post in re.findall(offsets["post_op"], html):
            post_id = re.search(offsets["post_id"], post).group()
            if (board, post_id, chan) in [item[:3] for item in cache]:
                logging.info("Parent post %s has already been handled." %
                             post_id)
                continue
            elif mode == "id":
                try:
                    url = offsets["link_prefix"] + re.search(
                        offsets["image_link"], post).group()
                    filename = re.search(offsets["file_name"], post).group()
                    logging.info("New parent post %s has been found!" %
                                 post_id)
                    data_queue.put((url, filename))
                except AttributeError:
                    logging.warning("Post %s was not handled properly." %
                                    post_id)
            elif mode == "ar":
                try:
                    name = re.search(offsets["poster_name"], post).group()
                    date = re.search(offsets["pub_date"], post).group()
                    time = re.search(offsets["pub_time"], post).group()
                    try:
                        filename = re.search(offsets["file_name"],
                                             post).group()
                    except AttributeError:
                        filename = "[No File]"
                    try:
                        title = re.search(offsets["post_title"], post).group()
                    except AttributeError:
                        title = "[No Title]"
                    try:
                        body = re.search(offsets["post_body"], post).group()
                    except AttributeError:
                        body = "[Empty Post]"
                    logging.info("New parent post %s has been found!" %
                                 post_id)
                    data_queue.put((post_id, None, name, date, time, filename,
                                    title, body))
                except AttributeError:
                    logging.warning("Post %s was not handled properly." %
                                    post_id)
            cache.append(
                (board, post_id, chan,
                 next(generate_urls(chan,
                                    board,
                                    post_id,
                                    ssl,
                                    thread_delimiter=thread_delimiter))))
        if thread_mode:
            for post in re.findall(offsets["post_reply"], html):
                parent_id = post_id
                post_id = re.search(offsets["post_id"], post).group()
                if (board, post_id, chan) in [item[:3] for item in cache]:
                    logging.info("Child post %s has already been handled." %
                                 post_id)
                    continue
                elif mode == "id":
                    try:
                        url = offsets["link_prefix"] + re.search(
                            offsets["image_link"], post).group()
                        filename = re.search(offsets["file_name"],
                                             post).group()
                        logging.info("New child post %s has been found!" %
                                     post_id)
                        data_queue.put((url, filename))
                    except AttributeError:
                        logging.warning("Post %s was not handled properly." %
                                        post_id)
                elif mode == "ar":
                    try:
                        name = re.search(offsets["poster_name"], post).group()
                        date = re.search(offsets["pub_date"], post).group()
                        time = re.search(offsets["pub_time"], post).group()
                        try:
                            filename = re.search(offsets["file_name"],
                                                 post).group()
                        except AttributeError:
                            filename = "[No File]"
                        try:
                            title = re.search(offsets["post_title"],
                                              post).group()
                        except AttributeError:
                            title = "[No Title]"
                        try:
                            body = re.search(offsets["post_body"],
                                             post).group()
                        except AttributeError:
                            body = "[Empty Post]"
                        logging.info("New child post %s has been found!" %
                                     post_id)
                        data_queue.put((post_id, parent_id, name, date, time,
                                        filename, title, body))
                    except AttributeError:
                        logging.warning("Post %s was not handled properly." %
                                        post_id)
                cache.append(
                    (board, post_id, chan,
                     next(generate_urls(chan,
                                        board,
                                        post_id,
                                        ssl,
                                        thread_delimiter=thread_delimiter))))
        if debug:
            break


def write_to_disk(mode, output, write_mode, data_queue, debug=False):
    """Thread for writing scraped data to disk."""
    logging.info("Starting...")
    if mode == "id":
        while True:
            url, filename = data_queue.get()
            while os.path.exists(os.path.join(output, filename)):
                filename = "(copy)" + filename
            urlretrieve(url, filename=os.path.join(output, filename))
            logging.info("File %s successfully downloaded!" % filename)
    else:
        with open(output, write_mode) as output_file:
            while True:
                post_id, parent_id, name, date, time, filename, title, body = data_queue.get(
                )
                if parent_id:
                    output_file.seek(0)
                else:
                    output_file.seek(0, 2)
                if len(title) > 0:
                    title += "\n"
                body = re.sub(r'<.*>', "", body)
                body = re.sub(r'&#039;', "'", body)
                body = re.sub(r'&quot;', "\"", body)
                body = re.sub(r'&amp;', "&", body)
                title = re.sub(r'<.*>', "", title)
                output_file.write(
                    "\n********************\n%s"
                    "Post ID: %s\nFile: %s\n%s"
                    "%s posted this on %s at %s\n"
                    "%s\n********************" % (
                        title, post_id, filename, "Reply to: %s\n" % parent_id
                        if parent_id else "", name, date, time, body))
                logging.info("Post %s successfully archived!" % post_id)
                output_file.seek(0, 0)
                if debug:
                    break


def load_cache(mode, dump_file):
    if dump_file is not None and os.path.exists(dump_file):
        with open(dump_file, "rb") as cache_load:
            try:
                cache = pickle.load(cache_load)
                if cache[0] != mode:
                    cache = []
                    logging.info("Incompatible cache file. Creating empty.")
                else:
                    cache = cache[1:]
                    logging.info("Cache file successfully loaded.")
            except pickle.PickleError:
                cache = []
                logging.warning("Incompatible cache file. Creating empty.")
            except EOFError:
                cache = []
                logging.warning("Empty cache file. Creating empty.")
    else:
        cache = []
        logging.info("Given cache did not exist. Creating empty.")
    return cache


def dump_cache(mode, cache, dump_file):
    """Called when the program exits to dump the post cache."""
    # Remove cached board pages.
    for index, item in enumerate(cache):
        if item[1] is None:
            del cache[index]
    if dump_file is None:
        logging.warning("Invalid cache dump path. Cache was lost.")
    else:
        with open(dump_file, "wb+") as cache_dump:
            pickle.dump([mode] + cache, cache_dump)
        logging.info("Cache dumped to \"%s\"." % dump_file)


def create_offsets(mode, chan=None):
    """Compile the regular expressions associated with the given imageboard."""
    if mode == "ar" and chan == "lainchan":
        offsets = {
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
    elif mode == "id" and chan == "lainchan":
        offsets = {
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
            "image_link": re.compile(
                r'((?<=File: <a href=")|(?<=" href=")).+?\.\w{3,4}(?=")'),
            "file_name": re.compile(r'(?<=\/)\d+?\.\w{3,4}')
        }
    elif mode == "tc" and chan == "lainchan":
        offsets = {
            "max_page": 7,
            "page_delimiter": "",
            "thread_delimiter": "res/"
        }
    elif mode == "ar" and chan == "4chan":
        offsets = {
            "max_page": 10,
            "page_delimiter": "",
            "thread_delimiter": "thread/",
            "board_initial": re.compile(r'(?<=boardTitle">)\/\S+?\/'),
            "post_op":
            re.compile(r'(?<=post op">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_reply":
            re.compile(r'(?<=post reply">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_id": re.compile(r'(?<=#p)\d+(?=")'),
            "file_name":
            re.compile(r'(?<=target="_blank">).+?\.\w{3,4}(?=</a>)'),
            "poster_name": re.compile(r'(?<=class="name">).*?(?=</span>)'),
            "post_title": re.compile(r'(?<=class="subject">).*?(?=</span>)'),
            "pub_date": re.compile(r'\d{2}\/\d{2}\/\d{2}\(\w{3}\)'),
            "pub_time": re.compile(r'\d{2}:\d{2}:\d{2}'),
            "post_body":
            re.compile(r'(?<="postMessage" id="m\d{8}">).+?(?=<\/block)')
        }
    elif mode == "id" and chan == "4chan":
        offsets = {
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
            "image_link": re.compile(
                r'((?<=File: <a href=")|(?<=" href=")).+?\.\w{3,4}(?=")'),
            "file_name":
            re.compile(r'(?<=target="_blank">).+?\.\w{3,4}(?=</a>)')
        }
    elif mode == "tc" and chan == "lainchan":
        offsets = {
            "max_page": 10,
            "page_delimiter": "",
            "thread_delimiter": "thread/"
        }
    elif mode == "ar":
        offsets = {
            "max_page": None,
            "page_delimiter": "",
            "thread_delimiter": "thread/",
            "board_initial": re.compile(r'(?<=boardTitle">)\/\S+?\/'),
            "post_op":
            re.compile(r'(?<=post op">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_reply":
            re.compile(r'(?<=post reply">)<div.+?\/blockquote>(?=<\/div>)'),
            "post_id": re.compile(r'(?<=#p)\d+(?=")'),
            "file_name":
            re.compile(r'(?<=target="_blank">).+?\.\w{3,4}(?=</a>)'),
            "poster_name": re.compile(r'(?<=class="name">).*?(?=</span>)'),
            "post_title": re.compile(r'(?<=class="subject">).*?(?=</span>)'),
            "pub_date": re.compile(r'\d{2}\/\d{2}\/\d{2}\(\w{3}\)'),
            "pub_time": re.compile(r'\d{2}:\d{2}:\d{2}'),
            "post_body":
            re.compile(r'(?<="postMessage" id="m\d{8}">).+?(?=<\/block)')
        }
    elif mode == "id":
        offsets = {
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
            "image_link": re.compile(
                r'((?<=File: <a href=")|(?<=" href=")).+?\.\w{3,4}(?=")'),
            "file_name":
            re.compile(r'(?<=target="_blank">).+?\.\w{3,4}(?=</a>)')
        }
    else:
        offsets = {
            "max_page": None,
            "page_delimiter": "",
            "thread_delimiter": "thread/"
        }
    return offsets


def main(mode,
         chan,
         combinations,
         refresh_rate=300,
         force_ssl=False,
         dump_file=None,
         no_video=False,
         output=".",
         write_mode=None,
         bottomfeed=False,
         dump=False,
         force=False,
         verbose=False):
    """Control function. Handles environment variables and threading."""
    logging.basicConfig(
        format="[%(threadName)-10s] %(levelname)s: %(message)s",
        level=logging.DEBUG if verbose else logging.WARNING)
    offsets = create_offsets(mode, chan)
    cache = load_cache(mode, dump_file)
    url_queue = queue.Queue(maxsize=0)
    html_queue = queue.Queue(maxsize=0)
    data_queue = queue.Queue(maxsize=0)
    connection_thread = threading.Thread(name="Connection Thread",
                                         target=get_url_content,
                                         daemon=True,
                                         args=(url_queue, html_queue, cache))
    scraper_thread = threading.Thread(name="Scraper Thread",
                                      target=scrape_html,
                                      daemon=True,
                                      args=(offsets, mode, chan, html_queue,
                                            data_queue, cache, force_ssl,
                                            offsets["thread_delimiter"]))
    write_thread = threading.Thread(name="Write Thread",
                                    target=write_to_disk,
                                    daemon=True,
                                    args=(mode, output, write_mode,
                                          data_queue))
    try:
        if any([combination[1] for combination in combinations]):
            temporary_cache = [item for item in cache]
            cache = []
        else:
            temporary_cache = []
        for board, thread in combinations:
            for url in generate_urls(chan,
                                     board,
                                     thread,
                                     force_ssl,
                                     bottomfeed,
                                     page_delimiter=offsets["page_delimiter"],
                                     max_page=offsets["max_page"]):
                cache.append((board, thread, chan, url))
        if mode == "tc":
            for item in cache:
                url_queue.put(item[3])
            exit(get_url_content(url_queue, html_queue, cache))
        connection_thread.start()
        scraper_thread.start()
        write_thread.start()
        while True:
            for item in cache:
                url_queue.put(item[3])
            time.sleep(refresh_rate)
    except KeyboardInterrupt:
        logging.critical("SIGINT received, quitting.")
        if dump:
            dump_cache(mode, cache, dump_file)
