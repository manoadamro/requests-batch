from threading import Thread
from typing import Any, List, Union

from requests import PreparedRequest, RequestException, Response, Session

from requests_batch.batch import BatchSession
from requests_batch.deserializer import BaseDeserializer

TResponse = Union[Response, RequestException, None]


class BaseStrategy:
    def __init__(self, **options: Any):
        self._options = options

    def execute(
        self,
        requests: List[PreparedRequest],
        raw_responses: List[TResponse],
        deserializer: BaseDeserializer,
    ) -> List[Any]:
        batch = BatchSession(requests=requests, responses=raw_responses)
        responses: List[Response] = self._execute(batch=batch)
        return [deserializer.deserialize(response) for response in responses]

    def do_request(self, request: PreparedRequest) -> TResponse:
        try:
            with Session() as session:
                response: Response = session.send(request=request, **self._options)
                response.raise_for_status()
                return response
        except RequestException as ex:
            return ex

    def _execute(self, batch: BatchSession) -> List[Response]:
        raise NotImplementedError


class Sequence(BaseStrategy):
    def _execute(self, batch: BatchSession) -> List[Response]:
        for index, request in enumerate(batch.requests):
            response = self.do_request(request=request)
            batch.add(index, response)
        return batch.validate()


class Threaded(BaseStrategy):
    def __init__(
        self, max_threads: int = 3, **options: Any,
    ):
        super(Threaded, self).__init__(**options)
        self._max_threads = max_threads
        self._threads = 0

    def _do_threaded_request(
        self, batch: BatchSession, request: PreparedRequest, index: int
    ) -> None:
        response = self.do_request(request=request)
        batch.add(index, response)
        self._threads -= 1

    def _execute(self, batch: BatchSession) -> List[Response]:
        index = 0
        while index < len(batch.requests):
            if self._threads >= self._max_threads:
                continue
            request = batch.requests[index]
            thread = Thread(
                target=self._do_threaded_request, args=(batch, request, index)
            )
            self._threads += 1
            thread.start()
            index += 1
        while self._threads > 0:
            continue
        return batch.validate()


class Strategy:
    sequence = Sequence
    threaded = Threaded
