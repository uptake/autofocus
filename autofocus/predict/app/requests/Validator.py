from abc import ABC, abstractmethod
from flask import jsonify, make_response, abort
from flask_api import status

class Validator(ABC):
    def __init__(self, request):
        self.request = request
        self.error = {}

    @abstractmethod
    def validate(self):
        pass

    def getError(self):
        return self.error
    
    def abort(self):
        abort(make_response(
            jsonify(
                status=status.HTTP_400_BAD_REQUEST,
                error=self.getError()
            ),
            status.HTTP_400_BAD_REQUEST
        ))
