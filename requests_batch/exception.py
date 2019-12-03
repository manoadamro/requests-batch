from typing import List, Union

from requests import PreparedRequest, RequestException, Response


class BatchRequestException(RequestException):
    def __init__(
        self,
        requests: List[PreparedRequest],
        responses: List[Union[Response, RequestException, None]],
        accepted: List[int],
        missing: List[int],
        failed: List[int],
    ):
        self._requests = requests
        self._responses = responses
        self._accepted = accepted
        self._missing = missing
        self._failed = failed

        super(BatchRequestException, self).__init__("")  # TODO
