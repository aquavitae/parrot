# -*- coding: utf-8 -*-

"""
Tests for `parrot`, a twitter-like fedd parser.
"""

from unittest import TestCase

import io
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
        self.assertEqual(dict(got), dict(expect))


class TestInputFiles(TestCase):

    """
    Test for various problems and variations with the input files.

    Specifically, these test the `read_file` function.
    """

    def test_with_filename(self):
        """
        `read_file` should accept a filename.
        """
        # No exception should be raised by this line
        list(parrot.read_file(users_file))

    def test_with_open_file(self):
        """
        `read_file` should accept an open file
        """
        with open(users_file, 'rb') as fh:
            # No exception should be raised by this line
            list(parrot.read_file(fh))

    def test_with_bytesio(self):
        """
        `read_file` should accept a BytesIO
        """
        fh = io.BytesIO(b'a\nb\nc')
        # No exception should be raised by this line
        list(parrot.read_file(fh))

    def test_with_stringio(self):
        """
        `read_file` should fail on a StringIO.
        """
        fh = io.StringIO('a\nb\nc')
        with self.assertRaises(TypeError):
            list(parrot.read_file(fh))

    def test_for_ascii_only_users(self):
        """
        Only ascii is allowed, so other characters should be stripped and
        a warning logged
        """
        text = io.BytesIO('a follows b\u200b'.encode())
        with self.assertLogs(parrot.log, 'WARN'):
            lines = list(parrot.read_file(text))
        self.assertEqual(lines, ['a follows b'])

    def test_linends(self):
        r"""
        Lines should be returned the same whether ending with \n , \r or \r\n
        """
        a = io.BytesIO(b'a\nb\nc')
        b = io.BytesIO(b'a\r\nb\rc')
        got_a = list(parrot.read_file(a))
        got_b = list(parrot.read_file(b))
        self.assertEqual(got_a, got_b)
