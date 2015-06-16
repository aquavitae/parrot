# -*- coding: utf-8 -*-

"""
Parrot - A twitter-like feed parser
"""

import codecs
import logging
import re
from collections import defaultdict

log = logging.getLogger()


def log_handler(err):
    """
    Handle unicode characters in the ascii input
    """
    log.warning(err)
    return ('', err.end)
codecs.register_error('log', log_handler)


def read_file(file):
    """
    Read an open file, check for errors and yield each line.

    `file` is expected to be either an open file in bytes mode or a filename.
    Each line is decoded to ascii and any unicode characters logged.
    """
    if isinstance(file, str):
        with open(file, 'rb') as fh:
            btext = fh.read()
    else:
        btext = file.read()
    btext = btext.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    for bline in btext.split(b'\n'):
        text = bline.decode('ascii', 'log')
        yield text


def parse_users(users_file):
    """
    Parse users and store them in a dict by poster.

    The output dict has poster names as keys and a set of their followers
    as values.  Each user, whether follower of poster is guaranteed to
    have an entry.
    """
    users = defaultdict(set)
    for line in read_file(users_file):
        m = re.search(r'^\s?(.+?)\sfollows(\s.*)?', line, flags = re.I)
        if m:
            follower, posters = m.groups()
            follower = follower.strip()
            if posters:
                for poster in posters.split(','):
                    poster = poster.strip()
                    users[poster].add(follower)
            # Make sure eacch followers has an entry, even if they
            # do not actually post
            users[follower]
    return users


def parse_tweets(tweets_file, users):
    """
    Parse tweets and return a list of tweets to be reported for each user.

    The output is a dict with follower names as keys and a list of
    tuples `(poster name, tweet)` as values.
    """
    tweets_per_user = defaultdict(list)
    for line in read_file(tweets_file):
        try:
            poster, tweet = line.split('>', 1)
        except ValueError:
            continue
        poster = poster.strip()
        tweet = tweet.strip()
        # Always add the tweet to the poster
        tweets_per_user[poster].append((poster, tweet))
        for follower in users[poster]:
            tweets_per_user[follower].append((poster, tweet))
    return tweets_per_user


def format_output(tweets_per_user, users):
    """
    Return formatted output for each user.
    """
    output = ''
    for follower in sorted(users):
        output += '{}\n'.format(follower)
        tweets = tweets_per_user[follower]
        for user, tweet in tweets:
            output += '\t@{}: {}\n'.format(user, tweet)
        output += '\n'
    return output


def main(users_file, tweets_file):
    """
    Given text files containing users and tweets, return the desired output.
    """
    # Parse users, and store them by poster
    users = parse_users(users_file)
    tweets_per_user = parse_tweets(tweets_file, users)
    output = format_output(tweets_per_user, users)
    return output
