# parrot
Exercise: Twitter-like feed parser

## Introduction

Parrot reads two input files, a list of users and followers and a list of
tweets, parses them and outputs the tweets for each user.  Users are listed
alphabetically and tweets are in posted order.  For example, given the
following input files:

* users.txt

    Ward follows Alan
    Alan follows Martin
    Ward follows Martin, Alan

* tweet.txt

    Alan> If you have a procedure with 10 parameters, you probably missed some.
    Ward> There are only two hard things in Computer Science: cache invalidation, naming things and off-by-1 errors.
    Alan> Random numbers should not be generated with a method chosen at random.

Print the following output:

  Alan
      @Alan: If you have a procedure with 10 parameters, you probably missed some.
      @Alan: Random numbers should not be generated with a method chosen at random.

  Martin

  Ward
      @Alan: If you have a procedure with 10 parameters, you probably missed some.
      @Ward: There are only two hard things in Computer Science: cache invalidation, naming things and off-by-1 errors.
      @Alan: Random numbers should not be generated with a method chosen at random.​


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
