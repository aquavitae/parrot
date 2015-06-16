# -*- coding: utf-8 -*-

"""
Tests for `parrot`, a twitter-like fedd parser.
"""

from unittest import TestCase

import os.path
from collections import defaultdict

from parrot import parrot


# Define this here to keep the test function itself neat
expected_main_functionality_output = """Alan
\t@Alan: If you have a procedure with 10 parameters, you probably missed some.
\t@Alan: Random numbers should not be generated with a method chosen at random.

Martin

Ward
\t@Alan: If you have a procedure with 10 parameters, you probably missed some.
\t@Ward: There are only two hard things in Computer Science: cache invalidation, naming things and off-by-1 errors.
\t@Alan: Random numbers should not be generated with a method chosen at random.
"""

root_path = os.path.dirname(__file__)
users_file = os.path.join(root_path, 'user.txt')
tweets_file = os.path.join(root_path, 'tweet.txt')


class TestPrescribedFiles(TestCase):

    """
    Test that the presribed input files work as defined.
    """

    def setUp(self):
        self.expected_users = defaultdict(set, {
            'Alan': {'Ward'},
            'Martin': {'Alan', 'Ward'},
            'Ward': set()
        })

    def test_functional(self):
        """
        This is a functional test that test that the final output is correct.
        """
        output = parrot.main(users_file=users_file, tweets_file=tweets_file)
        print('||' + output.replace(' ', '~') + '||')
        print('||' + expected_main_functionality_output.replace(' ', '~') + '||')
        self.assertEqual(output, expected_main_functionality_output)

    def test_parse_users(self):
        """
        Test the parse_users function.
        """
        got = parrot.parse_users(users_file)
        self.assertEqual(got, self.expected_users)

    def test_parse_tweets(self):
        """
        Test the parse_tweets function.
        """
        expect = defaultdict(list, {
            'Alan': [
                ('Alan', 'If you have a procedure with 10 parameters, you probably missed some.'),
                ('Alan', 'Random numbers should not be generated with a method chosen at random.')
            ],
            'Ward': [
                ('Alan', 'If you have a procedure with 10 parameters, you probably missed some.'),
                ('Ward', 'There are only two hard things in Computer Science: cache invalidation, naming things and off-by-1 errors.'),
                ('Alan', 'Random numbers should not be generated with a method chosen at random.')
            ]
        })
        self.maxDiff = None
        got = parrot.parse_tweets(tweets_file, self.expected_users)
        from pprint import pprint
        pprint(got)
        self.assertEqual(dict(got), dict(expect))
