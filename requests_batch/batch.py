from time import time
from typing import Any, Dict, List, Union

from requests import PreparedRequest, RequestException, Response

from requests_batch.exception import BatchRequestException

TResponse = Union[Response, RequestException, None]


class BatchSession:
    def __init__(
        self, requests: List[PreparedRequest], responses: List[TResponse],
    ):
        self._started = time()
        self._requests = requests
        self._responses = responses
        self._accepted: List[int] = []
        self._missing: List[int] = []
        self._failed: List[int] = []

    @property
    def requests(self) -> List[PreparedRequest]:
        return self._requests

    @property
    def responses(self) -> List[TResponse]:
        return self._responses

    def add(self, index: int, item: TResponse) -> None:
        if item is None:
            self._missing.append(index)
        if isinstance(item, Response):
            self._accepted.append(index)
        else:
            self._failed.append(index)
        self._responses[index] = item

    def validate(self) -> List[Any]:
        if len(self._missing) or len(self._failed):
            raise BatchRequestException(**self._pack())
        return self._responses

    def _pack(self) -> Dict[str, Any]:
        return dict(
            requests=self._requests,
            responses=self._responses,
            accepted=self._accepted,
            missing=self._missing,
            failed=self._failed,
        )
