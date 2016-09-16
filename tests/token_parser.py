import sys
import os
from itertools import chain
sys.path.insert(0,
                os.path.abspath(
                    os.path.join(
                        os.path.abspath(
                            os.path.dirname(__file__)),
                        '.')))
import unittest
from moira.tools.search import (PrefixWordsProducer, get_tokens_for_text, get_tokens_for_text_query, get_tokens_for_pattern,
    get_tokens_for_pattern_query, get_tokens_for_search_query, split_search_query)

from whoosh.analysis import RegexTokenizer


class PrefixWordsProducerTestCase(unittest.TestCase):

    analyzer = RegexTokenizer() | PrefixWordsProducer()
    text = u"one two 4569"

    def testPrefixProducer(self):
        self.assertItemsEqual(
            [t.text for t in self.analyzer(self.text)],
            ["o", "on", "one",
             "t", "tw", "two",
             "4", "45", "456", "4569"]
        )

    def testTokensIsTheOneObject(self):
        tokens = [t for t in self.analyzer(self.text)]
        first = tokens[0]
        self.assertTrue(all(first is t for t in tokens[1:]))


class TokenTestCase(unittest.TestCase):

    def testParseTokensFromText(self):
        self.assertItemsEqual(get_tokens_for_text_query(
            u"The! Token class has, no, methods 777#."),
            ["token", "class", "has", "no", "methods", "777"]
        )

        self.assertItemsEqual(get_tokens_for_text(
            u"The! Token class has no methods 777."),
            list(chain(
                ["t", "to", "tok", "toke", "token"],
                ["c", "cl", "cla", "clas", "class"],
                ["h", "ha", "has"],
                ["n", "no"],
                ["m", "me", "met", "meth", "metho", "method", "methods"],
                ["7", "77", "777"]
            ))
        )

        # stopwords: (`with`, `the`)
        self.assertItemsEqual(get_tokens_for_text_query(
            u''' ThE Working with editors/IDEs supporting "safe write"'''),
            ["working", "editors", "ides", "supporting", "safe", "write"]
        )

        # stopwords
        self.assertItemsEqual(get_tokens_for_text(
            u'''A is A'''),
            []
        )
        # stopwords
        self.assertItemsEqual(get_tokens_for_text_query(
            u'''A is A'''),
            []
        )

    def testParseTokensFromPattern(self):
        self.assertItemsEqual(get_tokens_for_pattern_query(
            u"The.toys.on.*.you89.My{frend, uiop}.42*"),
            ["the", "toys", "on", "you89", "my", "frend", "uiop", "42"]
        )

        self.assertItemsEqual(get_tokens_for_pattern(
            u'''A is A'''),
            ["a", "i", "is"]
        )
        self.assertItemsEqual(get_tokens_for_pattern_query(
            u'''A is A'''),
            ["a", "is"]
        )

    def testParseTokensFromSearchQuery(self):
        self.assertItemsEqual(get_tokens_for_search_query(
            u'###one two#a.b.c.d ####'),
            ['#one', 'two', '#a', 'b', 'c', 'd']
        )

    def testSplitTagsAndWords(self):
        tags, words = split_search_query(u'###one #one two two ')
        self.assertItemsEqual(tags, ['one'])
        self.assertItemsEqual(words, [(['two'], ['two'])])

        tags, words = split_search_query(u'###one two#a.b.c.d #### one')
        self.assertItemsEqual(tags, ['one', 'a'])

        tags, words = split_search_query(u'messages in dogs')
        self.assertItemsEqual(tags, [])
        self.assertItemsEqual(words, [
            (['messages'], ['messages']),
            ([], ['in']),
            (['dogs'], ['dogs']),
        ])
