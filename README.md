# parrot
Exercise: Twitter-like feed parser

[![Build Status](https://travis-ci.org/aquavitae/parrot.svg?branch=master)](https://travis-ci.org/aquavitae/parrot)
[![Coverage Status](https://coveralls.io/repos/aquavitae/parrot/badge.svg)](https://coveralls.io/r/aquavitae/parrot)

## Introduction

Parrot reads two input files, a list of users and followers and a list of
tweets, parses them and outputs the tweets for each user.  Users are listed
alphabetically and tweets are in posted order.  For example, given the
following input files:

* `users.txt`

  ```
  Ward follows Alan
  Alan follows Martin
  Ward follows Martin, Alan
  ```

* `tweet.txt`

  ```
  Alan> If you have a procedure with 10 parameters, you probably missed some.
  Ward> There are only two hard things in Computer Science: cache invalidation, naming things and off-by-1 errors.
  Alan> Random numbers should not be generated with a method chosen at random.
  ```

Print the following output:

  ```
  Alan
      @Alan: If you have a procedure with 10 parameters, you probably missed some.
      @Alan: Random numbers should not be generated with a method chosen at random.

  Martin

  Ward
      @Alan: If you have a procedure with 10 parameters, you probably missed some.
      @Ward: There are only two hard things in Computer Science: cache invalidation, naming things and off-by-1 errors.
      @Alan: Random numbers should not be generated with a method chosen at random.​

  ```

## Installation

Parrot required Python >=3.4 and can be installed using pip:

    pip install git+https://github.com/aquavitae/parrot

`pip` is normally part of a configured python installation, but if it is not available the code can be downloaded and installed using `python setup.py install`.  Alternatively, all functionality is contained in the file `parrot.py`, so it can simply be downloaded and run on its own.

## Usage

In its simplest form, parrot can be called as:

    parrot.py -u user.txt -t tweet.txt

and will print the list of posts as described above to `STDOUT`. Any errors or warning are logged to `STDERR`. Optionally, an output file may be specified using the `--output` or `-o` argument, in which case the list of posts is written to that file.  The output file is ASCII encoded and line endings are a single carriage return (i.e. `\n`).

`parrot -h` will show the following usage guide:

    parrot.py [-h] -u USERS -t TWEETS [-o OUTPUT]

    A twitter-like feed parser

    optional arguments:
      -h, --help                   show this help message and exit
      -u USERS, --users USERS      File containing a list of users and followers
      -t TWEETS, --tweets TWEETS   File containing a list of tweets
      -o OUTPUT, --output OUTPUT   File to write output to. If omitted, STDOUT will be used.

### Assumptions

* Only ascii characters can be used.  Any unicode characters will be dropped
  and an error logged.  Files are parsed line by line so a single entry
  cannot cross multiple lines.  Linux style `\n` and Windows style `\r\n`
  or `\r` line endings are valid.

* The *users* file is parsed by finding the first occurence on 'follows'
  (case-insensitive) surrounded by whitespace.  Posters are a comma-separated
  list on one line, and any ascii characters are allowed in a name although
  excess whitespace is stripped around names.  So the following would work
  as expected:

      Alan Johnson      FOLLOWS  Martin Smith,Alan_56, Follows

* The *tweets* file is parsed by finding the first occurence of '>' on each
  line and assuming that all text before is a user name and all text after
  is the tweet.  Excess whitespace is stripped around both.

* The user posting a tweet should exist, but if not a warning is logged.

* Tweets are processed in the order they are found in the input file, and
  this is assumed to be the order in which they are posted.

* Fatal exceptions (e.g. invalid filenames) are reflected by an unhandled
  python error.  This is assumed to be informative enough to show the problem.
