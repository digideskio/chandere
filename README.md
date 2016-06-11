![Chandere](https://raw.github.com/TsarFox/chandere/master/Chandere_Logo.png "Chandere")
======
## A utility programmed and maintained by [Jakob.](http://tsar-fox.com/)
Generalized scraper for Futaba-styled imageboards, such as 4chan. Capabilities range from downloading images to archiving entire boards.

Chandere is designed to work on both Python2 and Python3, and as of version 0.1.0 has no dependencies outside of the Python standard library.

Chandere is free software, licensed under the GNU General Public License.

=============
Main Features
=============

* Download images.
* Archive threads to plaintext.
* Scrape from multiple boards/threads at once.
* Caches threads that have been handled in the past.

============
Installation
============

Currently, the most reliable way to install Chandere is through Pip.

    # It is a good idea to update both pip and setuptools before installing.
    $ pip install --upgrade pip setuptools

    $ pip install --upgrade chandere

========
Tutorial
========

Chandere only really requires one argument to run. The following command will attempt to make a connection to http://boards.4chan.org/g/ and do nothing else.

    $ chandere /g/

Accessing multiple boards at once is just as simple, just add another one as an argument.

    $ chandere /g/ /3/

A specific thread can also be specified by placing the thread number after the board.

    $ chandere /g/51971506

Now with the basics of specifying where to scrape from, we can actually use the tool. To list all of the modes of operations Chandere supports, pass the "-lm" parameter.

    $ chandere -lm
    Available Modes of Operation: tc, id, ar

Descriptions of these modes are listed in the help page, they can be selected with the "-m" parameter. Let's use the example of downloading every image in a thread.

    $ chandere /g/51971506 -m id

This will download everything into the current working directory, though. Maybe we don't want that. We can specify the output path with the "-o" parameter.

    $ chandere /g/51971506 -m id -o Pictures\ Of\ Richard\ Stallman
    # For those unfamiliar, the backslash indicates an escaped space character. This outputs to the directory, "Pictures Of Richard Stallman".

Pretty neat, maybe we're a lainon and don't care much for 4chan, though. The imageboard can be specified with -c. An alias can be used if it is listed by the "-lc" parameter.

    $ chandere -lc
    Available Imageboard Aliases: lainchan, 4chan
    $ chandere /cyb/ -m id -o Cyberpunk -c lainchan

If the imageboard isn't a valid alias, it can still be passed with the "-c" parameter as long as it is in the form of an URL. This is not garunteed to work properly, though.

    $ chandere /c/ -c http://krautchan.net

That is the very basic usage. There are more parameters available, which can be listed with the "-h" parameter.


## TODO:
- [TODO](/docs/TODO.md)