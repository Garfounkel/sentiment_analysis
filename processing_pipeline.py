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


class BatchMaker(Preprocessor):
    def __init__(self, tokens, batch_size=10000):
        super().__init__(tokens)
        self.batch_size = batch_size
        self.tokens = iter(self.tokens)

    def __iter__(self):
        batch = []
        cont = True
        while cont:
            for _ in range(self.batch_size):
                try:
                    batch.append(next(self.tokens))
                except StopIteration:
                    cont = False
                    break
            yield batch


class Pipeline:
    def __init__(self, data, preprocessors=None):
        self.pipeline = data
        preprocessors = preprocessors or []
        for pproc in preprocessors:
            self.pipeline = pproc(self.pipeline)

    def __iter__(self):
        return iter(self.pipeline)
