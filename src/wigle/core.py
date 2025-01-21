import os
from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypedDict, Unpack

import httpx
from pydantic import BaseModel


def set_api_key(api_key: str) -> None:
    os.environ["WIGLE_API_KEY"] = api_key


class RequestParams(TypedDict, total=False):
    api_key: str
    timeout: int


type RequestMethod = Literal["GET", "POST", "PUT", "DELETE"]


def request(
    method: RequestMethod,
    url: str,
    params: dict,
    **kwargs: Unpack[RequestParams],
) -> httpx.Response:
    api_key = kwargs.get("api_key") or os.getenv("WIGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "Wigle API key not set. Use `wigle.set_api_key` function or set `WIGLE_API_KEY` environment variable."
        )
    headers = {
        "accept": "application/json",
        "Authorization": f"Basic {api_key}",
    }

    # Extract path params and format URL
    path_params = {}
    query_params = params.copy()
    for key in [k[1:-1] for k in url.split("/") if k.startswith("{") and k.endswith("}")]:
        if key in query_params:
            path_params[key] = query_params.pop(key)

    formatted_url = url.format(**path_params) if path_params else url

    response = httpx.request(
        method,
        formatted_url,
        params=query_params,
        headers=headers,
        timeout=kwargs.get("timeout", 60),
    )
    response.raise_for_status()
    return response


@dataclass
class Endpoint[T: BaseModel]:
    method: RequestMethod
    url: str
    response_model: type[T]

    def request(self, params: dict, **kwargs: Unpack[RequestParams]) -> httpx.Response:
        return request(self.method, self.url, params, **kwargs)

    def validate(self, data: dict) -> T:
        return self.response_model.model_validate(data)


endpoints: dict[type["Query"], Endpoint] = {}


def endpoint[T: Query](
    method: RequestMethod, url: str, response_model: type[BaseModel]
) -> Callable[[type[T]], type[T]]:
    def decorator(cls: type[T]) -> type[T]:
        endpoints[cls] = Endpoint(method, url, response_model)
        return cls

    return decorator


class Query[T: BaseModel](BaseModel, ABC):
    def result_or_error(self, **kwargs: Unpack[RequestParams]) -> T | httpx.HTTPStatusError:
        try:
            return self.request(**kwargs)
        except httpx.HTTPStatusError as exc:
            return exc

    def result_or_status(self, **kwargs: Unpack[RequestParams]) -> T | int:
        try:
            return self.request(**kwargs)
        except httpx.HTTPStatusError as exc:
            return exc.response.status_code

    def request(self, **kwargs: Unpack[RequestParams]) -> T:
        endpoint = endpoints.get(type(self))
        if not endpoint:
            raise ValueError(f"Endpoint not defined for {type(self)}")
        response = endpoint.request(self.model_dump(exclude_unset=True), **kwargs)
        response.raise_for_status()
        return endpoint.validate(response.json())

    @property
    def curl(self) -> str:
        endpoint = endpoints.get(type(self))
        if not endpoint:
            raise ValueError(f"Endpoint not defined for {type(self)}")

        # Extract path params and format URL
        params = self.model_dump(exclude_unset=True)
        path_params = {}
        query_params = params.copy()
        for key in [
            k[1:-1] for k in endpoint.url.split("/") if k.startswith("{") and k.endswith("}")
        ]:
            if key in query_params:
                path_params[key] = query_params.pop(key)

        formatted_url = endpoint.url.format(**path_params) if path_params else endpoint.url
        param_str = (
            "".join(f' -d {k}="{v}"' for k, v in query_params.items()) if query_params else ""
        )

        return f"curl -X {endpoint.method} {formatted_url}{param_str} -H 'Authorization: Basic {os.getenv('WIGLE_API_KEY')}'"
