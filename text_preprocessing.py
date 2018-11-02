from processing_pipeline import *

from keras.preprocessing.text import text_to_word_sequence
from tokenizer import tokenizer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer


class Tokenizer(Preprocessor):
    def __iter__(self):
        for token in self.tokens:
            yield list(self.__call__(token))


class KerasTokenizer(Tokenizer):
    def __call__(self, *args, **kwargs):
        return text_to_word_sequence(*args, **kwargs)


class TweetTokenizer(Tokenizer):
    def __init__(self, text):
        super().__init__(text)
        self.tkzer = tokenizer.TweetTokenizer(preserve_case=False, preserve_url=False)

    def __call__(self, *args, **kwargs):
        return self.tkzer.tokenize(*args, **kwargs)


class NLTKTokenizer(Tokenizer):
    def __call__(self, *args, **kwargs):
        return word_tokenize(*args, **kwargs)


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


"""
Testing the preprocessing classes
"""


def test_processor(ctor_list, data_source, name, corpus=False):
    print('Testing ' + name)
    for ctor in ctor_list:
        if corpus:
            print(list(CorpusWrapper(ctor, data_source)))
        else:
            print(list(ctor(data_source)))


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
        TweetTokenizer,
        FlatMap,
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
    texts = [
        'The quick brown fox jumped over the lazy dog. We are testing the preprocessors',
        'This is a test',
    ]
    tokenizers = [
        KerasTokenizer,
        TweetTokenizer,
        NLTKTokenizer,
    ]
    test_processor(tokenizers, texts, 'tokenizers')

    stemmers = [
        NLTKStemmer,
    ]
    test_processor(stemmers, KerasTokenizer(texts), 'stemmers', corpus=True)

    lemmatizers = [
        NLTKLemmatizer,
    ]
    test_processor(lemmatizers, CorpusWrapper(NLTKStemmer, KerasTokenizer(texts)), 'lemmatizers', corpus=True)

    test_pipeline()


if __name__ == "__main__":
    testing()
