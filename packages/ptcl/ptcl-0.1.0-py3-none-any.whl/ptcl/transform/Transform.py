from abc import ABC, abstractmethod

class Transform(ABC):

    """
        Parent class for all transforms.

        A transform, is a callable which acts as a node
        of a directed acyclic graph. Each transform, applies
        predefined operations to the input data, which is
        generally a string.
    """

    def __init__(self, children: list = None):
        self.children = children if children else []  # This is only a list to satisfy case-based routing

    @abstractmethod
    def transform(self, data):
        pass

    def __call__(self, data):
        """
            Evaluates the DAG structure defined by transforms.

            - If no children, stops and returns data
            - Assumes (data, ...) is the argument order
            - If more than one children, routes data assuming (index, data, ...) argument order

            Returns the last transformed data.
        """
        temp = self
        while True:
            data = temp.transform(data)
            if len(temp.children) == 0:
                break
            if len(temp.children) == 1:
                temp = temp.children[0]
            elif len(temp.children) > 1:
                temp = temp.children[data[0]]
                data = data[1:]
        return data

    def __rshift__(self, other):
        self.children.append(other)
        return other

