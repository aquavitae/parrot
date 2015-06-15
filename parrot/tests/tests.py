# -*- coding: utf-8 -*-

"""
Tests for `parrot`, a twitter-like fedd parser.
"""

from unittest import TestCase

from parrot import parrot


# Define this here to keep the test function itself neat
expected_main_functionality_output = """Alan
\t@Alan: If you have a procedure with 10 parameters, you probably missed some.
\t@Alan: Random numbers should not be generated with a method chosen at random.

Martin

Ward
\t@Alan: If you have a procedure with 10 parameters, you probably missed some.
\t@Ward: There are only two hard things in Computer Science: cache invalidation, naming things and off-by-1 errors.
\t@Alan: Random numbers should not be generated with a method chosen at random.​
"""


class TestMainFunctionality(TestCase):

    """
    These are functional tests then ensure the program as a whole is working.
    """

    def test_prescribed_files(self):
        """
        Test that the prescribed input files give the correct output.
        """
        output = parrot(users='users.txt', tweet='tweet.txt')
        self.assertEqual(output, expected_main_functionality_output)
