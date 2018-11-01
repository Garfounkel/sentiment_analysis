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
