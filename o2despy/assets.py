from abc import ABC


class IAssets(ABC):
    def __init__(self):
        self.__id = None

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value
