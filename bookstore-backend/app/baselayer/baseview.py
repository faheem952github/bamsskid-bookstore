from typing import Union

from fastapi import status
from fastapi.responses import JSONResponse


class FastResponder:
    """Base class for creating standardized API responses."""

    @staticmethod
    def make_response_body(success: bool = True, payload: dict = None, message: str = "") -> dict:
        """
        Creates a standardized response body.

        :param success: Indicates whether the response is successful.
        :param payload: Data to be included in the response.
        :param message: Message providing additional information about the response.
        :return: A dictionary containing the structured response.
        """
        return {
            "status": success,
            "data": payload if payload is not None else {},
            "message": message,
        }

    @staticmethod
    def send_response(success: bool = True, status_code: int = status.HTTP_200_OK,
                      payload: dict = None, message: str = "", **kwargs) -> JSONResponse:
        """
        Generates a JSON response based on provided parameters.

        :param success: Boolean indicating the success of the operation.
        :param status_code: HTTP status code of the response.
        :param payload: Data returned by the API.
        :param message: Message explaining the status.
        :return: JSONResponse object.
        """
        body = FastResponder.make_response_body(success, payload, message)
        return JSONResponse(content=body, status_code=status_code, **kwargs)

    # Convenience methods for common response scenarios
    @staticmethod
    def send_success_response(message: str, payload: Union[dict, list] = {}, **kwargs) -> JSONResponse:
        """Returns a success response."""
        return FastResponder.send_response(status_code=status.HTTP_200_OK, payload=payload, message=message, **kwargs)

    @staticmethod
    def send_created_response(message: str, payload: dict = None, **kwargs) -> JSONResponse:
        """Returns a response for successfully creating an item."""
        return FastResponder.send_response(status_code=status.HTTP_201_CREATED, payload=payload, message=message,
                                           **kwargs)

    @staticmethod
    def send_bad_request_response(message: str) -> JSONResponse:
        """Returns a bad request response."""
        return FastResponder.send_response(success=False, status_code=status.HTTP_400_BAD_REQUEST, message=message)

    @staticmethod
    def send_not_found_response(message: str = "Not found.") -> JSONResponse:
        """Returns a not found response."""
        return FastResponder.send_response(success=False, status_code=status.HTTP_404_NOT_FOUND, message=message)

    @staticmethod
    def send_internal_server_error_response(
            message: str = "System is down. Please try again in a while.") -> JSONResponse:
        """Returns an internal server error response."""
        return FastResponder.send_response(success=False, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                           message=message)
