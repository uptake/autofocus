from abc import ABC, abstractmethod
from flask import abort, jsonify, make_response
from flask_api import status


class Validator(ABC):
    """
    Validate given request

    Validator validates a given request based upon the abstract method validate.

    Parameters:
        request: Given request to validate
        error: Dict of errors
    """

    def __init__(self, request):
        """
        Constructor of Validator

        Store the request and create an empty error Dict.

        Parameters:
            request: Request to validate
        """
        self.request = request
        self.error = {}

    @abstractmethod
    def validate(self):
        """
        Validate the given request

        Returns:
            boolean: True if request is valid
        """
        pass

    def getError(self):
        """
        Return the error dictionary

        Returns:
            dict: The errors found during validation
        """
        return self.error
    
    def abort(self):
        """
        Abort with errors
        """
        abort(make_response(
            jsonify(
                status=status.HTTP_400_BAD_REQUEST,
                error=self.getError()
            ),
            status.HTTP_400_BAD_REQUEST
        ))
