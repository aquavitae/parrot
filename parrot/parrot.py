# -*- coding: utf-8 -*-

"""
Parrot - A twitter-like feed parser
"""

import codecs
import logging
import re
from collections import defaultdict

log = logging.getLogger()

# Template to use for printing each user block
tmpl_user = '{follower}\n{tweets}\n'

# Template to use for printing each line
tmpl_line = '\t@{poster}: {tweet}\n'


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
        elif len(line.strip()) > 0:
            log.warning("Users line %d: Badly formed line", lineno)
    return users


def parse_tweets(tweets_file, users):
    """
    Parse tweets and return a list of tweets to be reported for each user.

    The output is a dict with follower names as keys and a list of tweets
    formatted according to `tmpl_line`.
    """
    tweets_per_user = defaultdict(list)
    for line in read_file(tweets_file):
        try:
            poster, tweet = line.split('>', 1)
        except ValueError:
            continue
        poster = poster.strip()
        tweet = tweet.strip()
        formatted_tweet = tmpl_line.format(poster=poster, tweet=tweet)
        # Always add the tweet to the poster
        tweets_per_user[poster].append(formatted_tweet)
        for follower in users[poster]:
            tweets_per_user[follower].append(formatted_tweet)
    return tweets_per_user


def format_output(tweets_per_user, users):
    """
    Return formatted output for each user.
    """
    return ''.join(tmpl_user.format(
        follower=u,
        tweets=''.join(tweets_per_user[u])) for u in sorted(users)
    )


def main(users_file, tweets_file):
    """
    Given text files containing users and tweets, return the desired output.
    """
    # Parse users, and store them by poster
    users = parse_users(users_file)
    tweets_per_user = parse_tweets(tweets_file, users)
    output = format_output(tweets_per_user, users)
    return output
