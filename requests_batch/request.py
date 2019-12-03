from typing import Any, Callable, Iterable, List, Type, Union

from requests import PreparedRequest, Request, Response

from requests_batch.deserializer import BaseDeserializer, Deserializer
from requests_batch.strategy import BaseStrategy, Strategy

TDeserializer = Union[BaseDeserializer, Type[BaseDeserializer]]
TStrategy = Union[BaseStrategy, Type[BaseStrategy]]


class BatchRequest:
    def __init__(
        self,
        deserializer: TDeserializer = Deserializer.default,
        strategy: TStrategy = Strategy.sequence,
    ):
        self._requests: List[PreparedRequest] = []
        self._strategy: BaseStrategy = self._load_from_type(
            name="strategy", instance=strategy, klass=BaseStrategy
        )
        self._deserializer: BaseDeserializer = self._load_from_type(
            name="deserializer", instance=deserializer, klass=BaseDeserializer
        )

    def add(self, request: Request) -> PreparedRequest:
        prepared: PreparedRequest = request.prepare()
        self._requests.append(prepared)
        return prepared

    def add_range(self, requests: Iterable[Request]) -> List[PreparedRequest]:
        return [self.add(request=request) for request in requests]

    def send(self) -> List[Response]:
        count = len(self._requests)
        return self._strategy.execute(
            self._requests,
            [None for _ in range(count)],
            deserializer=self._deserializer,
        )

    @staticmethod
    def _load_from_type(name: str, instance: Any, klass: Type[Any]) -> Any:
        if isinstance(instance, klass):
            return instance
        if isinstance(instance, type) and issubclass(instance, klass):
            return instance()
        raise ValueError(
            f"{name} '{instance}' should be either '{klass.__name__}' or an instance of '{klass.__name__}'"
        )


def batch_request(
    *requests: Union[Request, Iterable[Request]],
    deserializer: TDeserializer = Deserializer.default,
    strategy: TStrategy = Strategy.sequence,
) -> List[Response]:
    def _flatten(obj: Any) -> Iterable[Request]:
        output: List[Request] = []
        if isinstance(obj, Iterable):
            for item in obj:
                output = [*output, *_flatten(item)]
        else:
            output = [obj]
        return output

    batch = BatchRequest(deserializer=deserializer, strategy=strategy)
    batch.add_range(requests=_flatten(obj=requests))
    return batch.send()


def _deferred_request(method: str) -> Callable[..., Request]:
    def _call(url: str, **kwargs: Any) -> Request:
        return Request(method=method.upper(), url=url, **kwargs)

    return _call


Get = _deferred_request("GET")
Put = _deferred_request("PUT")
Post = _deferred_request("POST")
Patch = _deferred_request("PATCH")
Delete = _deferred_request("DELETE")
Head = _deferred_request("HEAD")
Options = _deferred_request("OPTIONS")
