from keras.preprocessing.text import text_to_word_sequence
from tokenizer import tokenizer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer


class Tokenizer:
    def __init__(self, doc, corpus=False):
        if not corpus:
            self.docs = [doc]
        else:
            self.docs = doc

    def __iter__(self):
        for doc in self.docs:
            for token in self.__call__(doc):
                yield token


class KerasTokenizer(Tokenizer):
    def __call__(self, *args, **kwargs):
        return text_to_word_sequence(*args, **kwargs)


class TweetTokenizer(Tokenizer):
    def __init__(self, text, corpus=False):
        super().__init__(text, corpus)
        self.tkzer = tokenizer.TweetTokenizer(preserve_case=False, preserve_url=False)

    def __call__(self, *args, **kwargs):
        return self.tkzer.tokenize(*args, **kwargs)


class NLTKTokenizer(Tokenizer):
    def __call__(self, *args, **kwargs):
        return word_tokenize(*args, **kwargs)


class Preprocessor:
    def __init__(self, tokens):
        self.tokens = tokens

    def __iter__(self):
        for token in self.tokens:
            yield self.__call__(token)


class Stemmer(Preprocessor):
    pass


class NLTKStemmer(Stemmer):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.stmer = PorterStemmer()

    def __call__(self, *args, **kwargs):
        return self.stmer.stem(*args, **kwargs)


class Lemmatizer(Preprocessor):
    pass


class NLTKLemmatizer(Lemmatizer):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.lmer = WordNetLemmatizer()

    def __call__(self, *args, **kwargs):
        return self.lmer.lemmatize(*args, pos="v", **kwargs)


def test_processor(ctor_list, data_source, name):
    print('Testing ' + name)
    for ctor in ctor_list:
        print(set(ctor(data_source)))


class Pipeline:
    def __init__(self, data, preprocessors=None):
        self.pipeline = data
        preprocessors = preprocessors or []
        for pproc in preprocessors:
            self.pipeline = pproc(self.pipeline)

    def __iter__(self):
        return iter(self.pipeline)


"""
Testing the preprocessing classes
"""


def test_pipeline():
    """
    The Pipeline object aims at simplifying the preprocessing and the use of each preprocessor on a token stream.
    :return: None
    """
    print('Testing the pipeline')
    source = [
        'The quick brown fox jumped over the lazy dog.',
        'We are testing the preprocessors.',
        'This is a document',
    ]
    preprocessors = [
        lambda x: TweetTokenizer(x, corpus=True),
        NLTKStemmer,
        NLTKLemmatizer,
    ]
    pipeline = Pipeline(source, preprocessors)
    print(set(pipeline))


def testing():
    """
    Test functions for our tokenizer, stemmer and lemmatizer wrappers
    :return: None
    """
    text = 'The quick brown fox jumped over the lazy dog. We are testing the preprocessors'
    tokenizers = [
        KerasTokenizer,
        TweetTokenizer,
        NLTKTokenizer,
    ]
    test_processor(tokenizers, text, 'tokenizers')

    stemmers = [
        NLTKStemmer,
    ]
    test_processor(stemmers, KerasTokenizer(text), 'stemmers')

    lemmatizers = [
        NLTKLemmatizer,
    ]
    test_processor(lemmatizers, NLTKStemmer(KerasTokenizer(text)), 'lemmatizers')

    test_pipeline()


if __name__ == "__main__":
    testing()
