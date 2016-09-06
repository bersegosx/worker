from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter, StemmingAnalyzer


text_analyzer = StemmingAnalyzer() | LowercaseFilter() | StopFilter()
pattern_analyzer = RegexTokenizer(r"\w+") | LowercaseFilter()
search_query_analyzer = RegexTokenizer(r"#?\w+") | LowercaseFilter()


def get_tokens_for(analyzer):
    return lambda line: list(set([t.text for t in analyzer(line)]))

get_tokens_for_text = get_tokens_for(text_analyzer)
get_tokens_for_pattern = get_tokens_for(pattern_analyzer)
get_tokens_for_search_query = get_tokens_for(search_query_analyzer)


def split_search_query(query):
    tags, words = [], []
    for token in set(get_tokens_for_search_query(unicode(query))):
        if token.startswith('#'):
            tags.append(token[1:])
        else:
            words.append(token)

    words_result = []
    for word in words:
        text_tokens = get_tokens_for_text(word)
        pattern_tokens = get_tokens_for_pattern(word)
        words_result.append((text_tokens, pattern_tokens))

    return tags, words_result
