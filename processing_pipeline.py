class Preprocessor:
    def __init__(self, tokens):
        self.tokens = tokens

    def __iter__(self):
        for token in self.tokens:
            yield self.__call__(token)


class CorpusWrapper(Preprocessor):
    def __init__(self, preprocessor, tokens):
        super().__init__(tokens)
        self.preprocessor = preprocessor

    def __iter__(self):
        for token in self.tokens:
            res = list(self.preprocessor(token))
            yield res


class FlatMap(Preprocessor):
    def __iter__(self):
        for token in self.tokens:
            for tok in token:
                yield tok


class Batch:
    def __init__(self, source, len):
        self.source = source
        self.len = len
        self.stop = False

    def __len__(self):
        return self.len

    def __iter__(self):
        for _ in range(self.len):
            try:
                res = next(self.source)
            except StopIteration:
                self.stop = True
                break
            yield res


class BatchMaker(Preprocessor):
    def __init__(self, tokens, batch_size=1000):
        super().__init__(tokens)
        self.batch_size = batch_size
        self.tokens = iter(self.tokens)

    def __iter__(self):
        batch = Batch(self.tokens, self.batch_size)
        while not batch.stop:
            batch = Batch(batch.source, self.batch_size)
            yield batch


class Pipeline:
    def __init__(self, data, preprocessors=None):
        self.pipeline = data
        preprocessors = preprocessors or []
        for pproc in preprocessors:
            self.pipeline = pproc(self.pipeline)

    def __iter__(self):
        return iter(self.pipeline)


if __name__ == '__main__':
    from functools import partial                  # Nicer than lambdas
    from database_to_json import read_tweet_json
    from processing_pipeline import BatchMaker
    from processing_pipeline import Pipeline
    from text_preprocessing import TweetTokenizer, NLTKStemmer, NLTKLemmatizer, CorpusWrapper
    from gensim.models import Word2Vec

    input_stream = read_tweet_json(max=14)

    factories = [
        TweetTokenizer,
        partial(CorpusWrapper, NLTKStemmer),
        partial(CorpusWrapper, NLTKLemmatizer),
        BatchMaker,
    ]

    batch_pipeline = Pipeline(input_stream, factories)
    model = Word2Vec(next(iter(batch_pipeline)), size=300, sg=1, window=1, min_count=1, workers=16)

    for batch in batch_pipeline:
        print('new batch')
        for tweet in batch:
            print(tweet)
