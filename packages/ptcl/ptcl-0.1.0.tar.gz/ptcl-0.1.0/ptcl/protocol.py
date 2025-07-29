from .transform import Transform
import pickle

class Protocol:

    def __init__(self, transform: Transform):
        self.transform = transform

    def __call__(self, *args, **kwargs):
        return self.transform(*args, **kwargs)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

