from . import AbstractSocket

class Socket(AbstractSocket):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def transform(self, data):
        return self.protocol(data)


