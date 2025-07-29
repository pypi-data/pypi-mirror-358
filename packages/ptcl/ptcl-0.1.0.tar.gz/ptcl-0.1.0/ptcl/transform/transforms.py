from . import Transform

class RootTransform(Transform):

    def __init__(self):
        super().__init__()

    def transform(self, data):
        return data

class SplitText(Transform):

    def __init__(self, delimiter: str = " "):
        super().__init__()
        self.delimiter = delimiter

    def transform(self, data: str) -> list:
        return data.split(self.delimiter)

class ToString(Transform):

    def __init__(self, encoding: str = "utf-8"):
        super().__init__()
        self.encoding = encoding

    def transform(self, data: bytes) -> str:
        return data.decode(self.encoding)

class ToBytes(Transform):
    def __init__(self, encoding: str = "utf-8"):
        super().__init__()
        self.encoding = encoding

    def transform(self, data: str) -> bytes:
        return data.encode(self.encoding)

class ExtractToken(Transform):

    """
        Given a list of elements,
            - extracts one from the list
            - puts the rest in a list

        Returns:
            A tuple such that (rest, extracted)

    """

    def __init__(self, begin: bool = True):
        super().__init__()
        self.begin = begin

    def transform(self, data: list[str] | str):
        return (data[1:], data[0]) if self.begin else (data[:-1], data[-1])

class RouteOnKeyword(Transform):

    def __init__(self, keywords: list[str], children: list[Transform] = None):
        super().__init__(children)
        self.keywords = keywords

    def transform(self, data_keyword_tuple: tuple):
        data, keyword = data_keyword_tuple[:-1], data_keyword_tuple[-1]
        return self.keywords.index(keyword), data

class CountPasses(Transform):

    def __init__(self):
        super().__init__()
        self.count = 0

    def transform(self, data):
        self.count += 1
        return data

class ReverseTransform(Transform):

    def __init__(self):
        super().__init__()

    def transform(self, data):
        return data[::-1]

class CombineTransform(Transform):

    def __init__(self, combiner: str = " "):
        super().__init__()
        self.combiner = combiner

    def transform(self, data):
        return self.combiner.join(data)
