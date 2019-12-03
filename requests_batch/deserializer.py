from typing import Any, Dict, List, Union

from requests import Response

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class BaseDeserializer:
    def deserialize(self, response: Response) -> Any:
        raise NotImplementedError


class Default(BaseDeserializer):
    def deserialize(self, response: Response) -> Response:
        return response


class Json(BaseDeserializer):
    def __init__(self, **options: Any):
        self._options = options

    def deserialize(self, response: Response) -> Union[List[Any], Dict[str, Any]]:
        data: Union[List[Any], Dict[str, Any]] = response.json(**self._options)
        return data


class Text(BaseDeserializer):
    def deserialize(self, response: Response) -> str:
        return response.text


class Bs4(Text):
    def __init__(self, **options: Any):
        if BeautifulSoup is None:
            raise ImportError(
                "beautiful soup is not installed. "
                "use 'pip install bs4' to install beautiful soup"
                "or install requests_batch with bs4 with 'pip install requests-batch[bs4]'"
            )
        self._options = options

    def deserialize(self, response: Response) -> BeautifulSoup:
        text = super(Bs4, self).deserialize(response=response)
        response = BeautifulSoup(markup=text, **self._options)
        return response


class Deserializer:
    default = Default
    json = Json
    text = Text
    bs4 = Bs4
