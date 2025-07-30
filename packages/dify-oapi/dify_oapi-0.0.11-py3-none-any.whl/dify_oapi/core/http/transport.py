import asyncio
import json
import math
import time
from collections.abc import AsyncGenerator, Coroutine, Generator
from typing import Literal, overload

import httpx

from dify_oapi.core.const import APPLICATION_JSON, AUTHORIZATION, SLEEP_BASE_TIME, UTF_8
from dify_oapi.core.json import JSON
from dify_oapi.core.log import logger
from dify_oapi.core.misc import HiddenText
from dify_oapi.core.model.base_request import BaseRequest
from dify_oapi.core.model.base_response import BaseResponse
from dify_oapi.core.model.config import Config
from dify_oapi.core.model.raw_response import RawResponse
from dify_oapi.core.model.request_option import RequestOption
from dify_oapi.core.type import T


class Transport:
    @staticmethod
    @overload
    def execute(
        conf: Config,
        req: BaseRequest,
        *,
        stream: Literal[True],
        option: RequestOption | None,
    ) -> Generator[bytes, None, None]: ...

    @staticmethod
    @overload
    def execute(conf: Config, req: BaseRequest) -> BaseResponse: ...

    @staticmethod
    @overload
    def execute(conf: Config, req: BaseRequest, *, option: RequestOption | None) -> BaseResponse: ...

    @staticmethod
    @overload
    def execute(
        conf: Config,
        req: BaseRequest,
        *,
        unmarshal_as: type[T],
        option: RequestOption | None,
    ) -> T: ...

    @staticmethod
    def execute(
        conf: Config,
        req: BaseRequest,
        *,
        stream: bool = False,
        unmarshal_as: type[T] | type[BaseResponse] | None = None,
        option: RequestOption | None = None,
    ):
        if unmarshal_as is None:
            unmarshal_as = BaseResponse
        if option is None:
            option = RequestOption()
        # 拼接url
        url: str = _build_url(conf.domain, req.uri, req.paths)
        # 组装header
        headers: dict[str, str] = _build_header(req, option)
        json_, files, data = None, None, None
        if req.files:
            # multipart/form-data
            files = req.files
            if req.body is not None:
                data = json.loads(JSON.marshal(req.body))
        elif req.body is not None:
            # application/json
            json_ = json.loads(JSON.marshal(req.body))

        if req.http_method is None:
            raise RuntimeError("HTTP method is required")
        http_method_name = str(req.http_method.name)
        if stream:

            def _stream_generator() -> Generator[bytes, None, None]:
                with (
                    httpx.Client() as _client,
                    _client.stream(
                        http_method_name,
                        url,
                        headers=headers,
                        params=tuple(req.queries),
                        json=json_,
                        data=data,
                        files=files,
                        timeout=conf.timeout,
                    ) as async_response,
                ):
                    logger.debug(
                        f"{http_method_name} {url} {async_response.status_code}, "
                        f"headers: {JSON.marshal(headers)}, "
                        f"params: {JSON.marshal(req.queries)}, "
                        f"stream response"
                    )
                    yield from async_response.iter_bytes()

            return _stream_generator()
        with httpx.Client() as client:
            # 通过变量赋值，防止动态调整 max_retry_count 出现并发问题
            retry_count = conf.max_retry_count
            for i in range(0, retry_count + 1):
                # 采用指数避让策略
                if i != 0:
                    sleep_time = _get_sleep_time(i)
                    logger.info(f"in-request: sleep {sleep_time}s")
                    time.sleep(sleep_time)
                try:
                    response = client.request(
                        http_method_name,
                        url,
                        headers=headers,
                        params=tuple(req.queries),
                        json=json_,
                        data=data,
                        files=files,
                        timeout=conf.timeout,
                    )
                    break
                except httpx.RequestError as e:
                    if i < retry_count:
                        logger.info(
                            f"in-request: retry success "
                            f"{http_method_name} {url}"
                            f"{f', headers: {JSON.marshal(headers)}' if headers else ''}"
                            f"{f', params: {JSON.marshal(req.queries)}' if req.queries else ''}"
                            f"{f', body: {JSON.marshal(_merge_dicts(json_, files, data))}' if json_ or files or data else ''}"
                            f"{f', exp: {e}'}"
                        )
                        continue
                    logger.info(
                        f"in-request: retry fail "
                        f"{http_method_name} {url}"
                        f"{f', headers: {JSON.marshal(headers)}' if headers else ''}"
                        f"{f', params: {JSON.marshal(req.queries)}' if req.queries else ''}"
                        f"{f', body: {JSON.marshal(_merge_dicts(json_, files, data))}' if json_ or files or data else ''}"
                        f"{f', exp: {e}'}"
                    )
                    raise e
            logger.debug(
                f"{http_method_name} {url} {response.status_code}"
                f"{f', headers: {JSON.marshal(headers)}' if headers else ''}"
                f"{f', params: {JSON.marshal(req.queries)}' if req.queries else ''}"
                f"{f', body: {JSON.marshal(_merge_dicts(json_, files, data))}' if json_ or files or data else ''}"
            )

            raw_resp = RawResponse()
            raw_resp.status_code = response.status_code
            raw_resp.headers = dict(response.headers)
            raw_resp.content = response.content
            return _unmarshaller(raw_resp, unmarshal_as)


class ATransport:
    @staticmethod
    @overload
    def aexecute(
        conf: Config,
        req: BaseRequest,
        *,
        stream: Literal[True],
        option: RequestOption | None,
    ) -> Coroutine[None, None, AsyncGenerator[bytes, None]]: ...

    @staticmethod
    @overload
    def aexecute(conf: Config, req: BaseRequest) -> Coroutine[None, None, BaseResponse]: ...

    @staticmethod
    @overload
    def aexecute(
        conf: Config, req: BaseRequest, *, option: RequestOption | None
    ) -> Coroutine[None, None, BaseResponse]: ...

    @staticmethod
    @overload
    def aexecute(
        conf: Config,
        req: BaseRequest,
        *,
        unmarshal_as: type[T],
        option: RequestOption | None,
    ) -> Coroutine[None, None, T]: ...

    @staticmethod
    async def aexecute(
        conf: Config,
        req: BaseRequest,
        *,
        stream: bool = False,
        unmarshal_as: type[T] | type[BaseResponse] | None = None,
        option: RequestOption | None = None,
    ):
        if unmarshal_as is None:
            unmarshal_as = BaseResponse
        if option is None:
            option = RequestOption()

        # 拼接url
        url: str = _build_url(conf.domain, req.uri, req.paths)

        # 组装header
        headers: dict[str, str] = _build_header(req, option)

        json_, files, data = None, None, None
        if req.files:
            # multipart/form-data
            files = req.files
            if req.body is not None:
                data = json.loads(JSON.marshal(req.body))
        elif req.body is not None:
            # application/json
            json_ = json.loads(JSON.marshal(req.body))
        if req.http_method is None:
            raise RuntimeError("Http method is required")
        http_method_name = str(req.http_method.name)
        if stream:

            async def _async_stream_generator():
                async with (
                    httpx.AsyncClient() as _client,
                    _client.stream(
                        http_method_name,
                        url,
                        headers=headers,
                        params=tuple(req.queries),
                        json=json_,
                        data=data,
                        files=files,
                        timeout=conf.timeout,
                    ) as async_response,
                ):
                    logger.debug(
                        f"{http_method_name} {url} {async_response.status_code}, "
                        f"headers: {JSON.marshal(headers)}, "
                        f"params: {JSON.marshal(req.queries)}, "
                        f"stream response"
                    )
                    async for chunk in async_response.aiter_bytes():
                        yield chunk

            return _async_stream_generator()
        async with httpx.AsyncClient() as client:
            # 通过变量赋值，防止动态调整 max_retry_count 出现并发问题
            retry_count = conf.max_retry_count
            for i in range(0, retry_count + 1):
                # 采用指数避让策略
                if i != 0:
                    sleep_time = _get_sleep_time(i)
                    logger.info(f"in-request: sleep {sleep_time}s")
                    await asyncio.sleep(sleep_time)
                try:
                    response = await client.request(
                        http_method_name,
                        url,
                        headers=headers,
                        params=tuple(req.queries),
                        json=json_,
                        data=data,
                        files=files,
                        timeout=conf.timeout,
                    )
                    break
                except httpx.RequestError as e:
                    if i < retry_count:
                        logger.info(
                            f"in-request: retry success "
                            f"{http_method_name} {url}"
                            f"{f', headers: {JSON.marshal(headers)}' if headers else ''}"
                            f"{f', params: {JSON.marshal(req.queries)}' if req.queries else ''}"
                            f"{f', body: {JSON.marshal(_merge_dicts(json_, files, data))}' if json_ or files or data else ''}"
                            f"{f', exp: {e}'}"
                        )
                        continue
                    logger.info(
                        f"in-request: retry fail "
                        f"{http_method_name} {url}"
                        f"{f', headers: {JSON.marshal(headers)}' if headers else ''}"
                        f"{f', params: {JSON.marshal(req.queries)}' if req.queries else ''}"
                        f"{f', body: {JSON.marshal(_merge_dicts(json_, files, data))}' if json_ or files or data else ''}"
                        f"{f', exp: {e}'}"
                    )
                    raise e

            logger.debug(
                f"{http_method_name} {url} {response.status_code}"
                f"{f', headers: {JSON.marshal(headers)}' if headers else ''}"
                f"{f', params: {JSON.marshal(req.queries)}' if req.queries else ''}"
                f"{f', body: {JSON.marshal(_merge_dicts(json_, files, data))}' if json_ or files or data else ''}"
            )

            raw_resp = RawResponse()
            raw_resp.status_code = response.status_code
            raw_resp.headers = dict(response.headers)
            raw_resp.content = response.content

            return _unmarshaller(raw_resp, unmarshal_as)


def _build_url(domain: str | None, uri: str | None, paths: dict[str, str] | None) -> str:
    if domain is None:
        raise RuntimeError("domain is required")
    if uri is None:
        raise RuntimeError("uri is required")
    for key, value in (paths or {}).items():
        uri = uri.replace(":" + key, value)
    if domain.endswith("/") and uri.startswith("/"):
        domain = domain[:-1]
    return domain + uri


def _build_header(request: BaseRequest, option: RequestOption) -> dict[str, str]:
    headers = request.headers
    # 附加header
    if option.headers is not None:
        for key in option.headers:
            headers[key] = option.headers[key]
    if option.api_key is not None:
        headers[AUTHORIZATION] = HiddenText(f"Bearer {option.api_key}", redacted="****")
    return headers


def _merge_dicts(*dicts):
    res = {}
    for d in dicts:
        if d is not None:
            res.update(d)
    return res


def _unmarshaller(raw_resp: RawResponse, unmarshal_as: type[T]) -> T:
    if raw_resp.status_code is None:
        raise RuntimeError("status_code is required")
    if raw_resp.content is None:
        raise RuntimeError("status_code is required")
    resp = unmarshal_as()
    if raw_resp.content_type is not None and raw_resp.content_type.startswith(APPLICATION_JSON):
        content = str(raw_resp.content, UTF_8)
        if content != "":
            try:
                resp = JSON.unmarshal(content, unmarshal_as)
            except Exception as e:
                logger.error(f"Failed to unmarshal to {unmarshal_as} from {content}")
                raise e
    resp.raw = raw_resp
    # if 200 <= raw_resp.status_code < 300:
    #     resp.code = "success"
    return resp


def _get_sleep_time(retry_count: int):
    sleep_time = SLEEP_BASE_TIME * math.pow(2, retry_count - 1)
    # if sleep_time > 60:
    #     sleep_time = 60
    # if raw_resp and (raw_resp.status_code == 429 or raw_resp.status_code == 503) and 'retry-after' in raw_resp.headers:
    #     try:
    #         sleep_time = max(int(raw_resp.headers['retry-after']), sleep_time)
    #     except Exception as e:
    #         logger.warning('try to parse retry-after from headers error: {}'.format(e))
    return sleep_time
