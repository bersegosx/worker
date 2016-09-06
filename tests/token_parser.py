import sys
import os
sys.path.insert(0,
                os.path.abspath(
                    os.path.join(
                        os.path.abspath(
                            os.path.dirname(__file__)),
                        '.')))
import unittest
from moira.tools.search import get_tokens_for_text, get_tokens_for_pattern, get_tokens_for_search_query, split_search_query


class TokenTestCase(unittest.TestCase):

    def testParseTokensFromText(self):
        self.assertItemsEqual(get_tokens_for_text(
            u"The! Token class has no methods 777."),
            ["token", "class", "ha", "no", "method", "777"]
        )
        self.assertItemsEqual(get_tokens_for_text(
            u'''Working with editors/IDEs supporting "safe write"'''),
            ["work", "editor", "id", "support", "safe", "write"]
        )
        self.assertItemsEqual(get_tokens_for_text(
            u'''A is A'''),
            []
        )

    def testParseTokensFromPattern(self):
        self.assertItemsEqual(get_tokens_for_pattern(
            u"The.toys.on.*.you89.My{frend, uiop}.42*"),
            ["the", "toys", "on", "you89", "my", "frend", "uiop", "42"]
        )
        self.assertItemsEqual(get_tokens_for_pattern(
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
            (['messag'], ['messages']),
            ([], ['in']),
            (['dog'], ['dogs']),
        ])
