# -*- coding: utf-8 -*-

"""
Parrot - A twitter-like feed parser
"""


from collections import defaultdict


def parse_users(users_file):
    """
    Parse users and store them in a dict by poster.

    The output dict has poster names as keys and a set of their followers
    as values.  Each user, whether follower of poster is guaranteed to
    have an entry.
    """
    users = defaultdict(set)
    with open(users_file, 'r') as fh:
        for line in fh:
            follower, _, posters = line.split(' ', 2)
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
    with open(tweets_file, 'r') as fh:
        for line in fh:
            poster, tweet = line.split('>', 1)
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
