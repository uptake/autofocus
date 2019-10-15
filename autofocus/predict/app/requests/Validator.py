from abc import ABC, abstractmethod

class Validator(ABC):
    def __init__(self, request):
        self.request = request
        self.error = {}

    @abstractmethod
    def validate(self):
        pass

    def getError(self):
        return self.error
