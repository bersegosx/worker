from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter
from whoosh.analysis.filters import Filter


class PrefixWordsProducer(Filter):

    def __call__(self, tokens):
        for t in tokens:
            text = t.text
            for pos in range(1, len(text) + 1):
                t.text = text[:pos]
                yield t


text_analyzer_query = RegexTokenizer() | LowercaseFilter() | StopFilter()
text_analyzer_index = text_analyzer_query | PrefixWordsProducer()

pattern_analyzer_query = RegexTokenizer(r"\w+") | LowercaseFilter()
pattern_analyzer_index = pattern_analyzer_query | PrefixWordsProducer()

search_query_analyzer = RegexTokenizer(r"#?\w+") | LowercaseFilter()


def get_tokens_for(analyzer):
    return lambda line: list(set([t.text for t in analyzer(line)]))

get_tokens_for_text          = get_tokens_for(text_analyzer_index)
get_tokens_for_text_query    = get_tokens_for(text_analyzer_query)
get_tokens_for_pattern       = get_tokens_for(pattern_analyzer_index)
get_tokens_for_pattern_query = get_tokens_for(pattern_analyzer_query)
get_tokens_for_search_query  = get_tokens_for(search_query_analyzer)


def split_search_query(query):
    tags, words = [], []
    for token in set(get_tokens_for_search_query(unicode(query))):
        if token.startswith('#'):
            tags.append(token[1:])
        else:
            words.append(token)

    words_result = []
    for word in words:
        text_tokens = get_tokens_for_text_query(word)
        pattern_tokens = get_tokens_for_pattern_query(word)
        words_result.append((text_tokens, pattern_tokens))

    return tags, words_result
