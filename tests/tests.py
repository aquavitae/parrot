# -*- coding: utf-8 -*-

"""
Tests for `parrot`, a twitter-like fedd parser.
"""

from unittest import TestCase

import io
import os.path
import subprocess

from collections import defaultdict

import parrot


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
                '\t@Alan: If you have a procedure with 10 parameters, you probably missed some.\n',
                '\t@Alan: Random numbers should not be generated with a method chosen at random.\n',
            ],
            'Ward': [
                '\t@Alan: If you have a procedure with 10 parameters, you probably missed some.\n',
                '\t@Ward: There are only two hard things in Computer Science: cache invalidation, naming things and off-by-1 errors.\n',
                '\t@Alan: Random numbers should not be generated with a method chosen at random.\n',
            ]
        })
        got = parrot.parse_tweets(tweets_file, self.expected_users)
        self.assertEqual(dict(got), dict(expect))

    def test_commandline(self):
        prog = os.path.join(root_path, '..', 'parrot.py')
        args = [prog, '-u', users_file, '-t', tweets_file]
        got = subprocess.check_output(args)
        # subprocess.check_args output is bytes and always has an extra newline
        got = got.decode('ascii')[:-1]
        self.assertEqual(got, expected_main_functionality_output)


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


class TestParseUsersFormat(TestCase):

    """
    Test different permutations of the users file format
    """

    def test_single_line(self):
        users = io.BytesIO(b'a follows b, c')
        got = dict(parrot.parse_users(users))
        self.assertEqual(got, {'b': {'a'}, 'a': set(), 'c': {'a'}})

    def test_blank_lines(self):
        users = io.BytesIO(b'a follows b\n\n\n\nc follows d')
        got = dict(parrot.parse_users(users))
        self.assertEqual(got, {'b': {'a'}, 'd': {'c'}, 'a': set(), 'c': set()})

    def test_caps(self):
        users = io.BytesIO(b'A FOLLOWS B')
        got = dict(parrot.parse_users(users))
        self.assertEqual(got, {'B': {'A'}, 'A': set()})

    def test_multiple_spaces(self):
        users = io.BytesIO(b'a    follows     b   ,   c ')
        got = dict(parrot.parse_users(users))
        self.assertEqual(got, {'b': {'a'}, 'a': set(), 'c': {'a'}})

    def test_other_symbols(self):
        users = io.BytesIO(b'\\a_% follows \\n2')
        got = dict(parrot.parse_users(users))
        self.assertEqual(got, {'\\n2': {'\\a_%'}, '\\a_%': set()})

    def test_names_follows(self):
        users = io.BytesIO(b'follows follows follows')
        got = dict(parrot.parse_users(users))
        self.assertEqual(got, {'follows': {'follows'}})

    def test_names_follows2(self):
        users = io.BytesIO(b'a follows b, follows, c')
        got = dict(parrot.parse_users(users))
        self.assertEqual(got, {'b': {'a'}, 'follows': {'a'}, 'c': {'a'}, 'a': set()})

    def test_missing_poster(self):
        users = io.BytesIO(b'a follows')
        got = dict(parrot.parse_users(users))
        self.assertEqual(got, {'a': set()})

    def test_missing_follower(self):
        """
        This line cannot be parsed
        """
        users = io.BytesIO(b'follows b')
        with self.assertLogs(parrot.log, 'WARN'):
            got = dict(parrot.parse_users(users))
        self.assertEqual(got, {})

    def test_double_names(self):
        users = io.BytesIO(b'a b follows b c, c d')
        got = dict(parrot.parse_users(users))
        self.assertEqual(got, {'b c': {'a b'}, 'c d': {'a b'}, 'a b': set()})

    def test_no_spaces(self):
        """
        This should not parse, since "afollowsb" could be someone's name.
        """
        users = io.BytesIO(b'afollowsb')
        with self.assertLogs(parrot.log, 'WARN'):
            got = dict(parrot.parse_users(users))
        self.assertEqual(got, {})


class TestParseTweetsFormat(TestCase):

    """
    Test different permutations of the tweets file format
    """

    def test_single_line(self):
        tweets = io.BytesIO(b'a> post')
        users = {'a': set()}
        got = dict(parrot.parse_tweets(tweets, users))
        self.assertEqual(got, {'a': ['\t@a: post\n']})

    def test_blanks_and_spaces(self):
        tweets = io.BytesIO(b'  a > post  \n\n     \n\na>another  post\n\n')
        users = {'a': set()}
        got = dict(parrot.parse_tweets(tweets, users))
        self.assertEqual(got, {'a': ['\t@a: post\n', '\t@a: another  post\n']})

    def test_symbols(self):
        tweets = io.BytesIO(b'a>>post>:')
        users = {'a': set()}
        got = dict(parrot.parse_tweets(tweets, users))
        self.assertEqual(got, {'a': ['\t@a: >post>:\n']})

    def test_missing_post(self):
        tweets = io.BytesIO(b'a>')
        users = {'a': set()}
        got = dict(parrot.parse_tweets(tweets, users))
        self.assertEqual(got, {'a': ['\t@a: \n']})

    def test_missing_poster(self):
        tweets = io.BytesIO(b'> post')
        users = {'a': set()}
        with self.assertLogs(parrot.log, 'WARN'):
            got = dict(parrot.parse_tweets(tweets, users))
        self.assertEqual(got, {})

    def test_no_valid_poster(self):
        tweets = io.BytesIO(b'a> post')
        users = {'b': set()}
        with self.assertLogs(parrot.log, 'ERROR'):
            got = dict(parrot.parse_tweets(tweets, users))
        self.assertEqual(got, {})
