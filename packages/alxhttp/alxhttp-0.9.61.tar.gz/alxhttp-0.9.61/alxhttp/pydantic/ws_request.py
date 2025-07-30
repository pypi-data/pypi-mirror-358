from typing import AsyncIterator, Callable, NamedTuple, Type, TypeVar

import aiohttp
import pydantic
from aiohttp import WSMsgType, web

from alxhttp.pydantic.basemodel import BaseModel, ErrorModel

ErrorType = TypeVar('ErrorType', bound=ErrorModel)
WSRequestType = TypeVar('WSRequestType', bound='WSRequest')
ServerMsgType = TypeVar('ServerMsgType')
ClientMsgType = TypeVar('ClientMsgType', bound=BaseModel)
ClientMsgLoadsType = Callable[[str], ClientMsgType]


class TypedWSMessage[ClientMsgType](NamedTuple):
  type: WSMsgType
  data: ClientMsgType | None


class WSRequest[MatchInfoType, QueryType, ServerMsgType](BaseModel):
  _web_request: web.Request = pydantic.PrivateAttr()
  _ws: web.WebSocketResponse = pydantic.PrivateAttr()
  _client_msg_loads: ClientMsgLoadsType = pydantic.PrivateAttr()
  _server_msg: Type[ServerMsgType] = pydantic.PrivateAttr()
  match_info: MatchInfoType
  query: QueryType

  @classmethod
  async def from_request(cls: Type[WSRequestType], request: web.Request, server_msg: Type[ServerMsgType], client_msg_loads: ClientMsgLoadsType) -> WSRequestType:
    m = cls.model_validate(
      {
        'match_info': request.match_info,
        'query': dict(request.query),
      }
    )
    m._web_request = request
    m._server_msg = server_msg
    m._client_msg_loads = client_msg_loads
    return m

  async def prepare_ws(self) -> None:
    self._ws = web.WebSocketResponse()
    await self._ws.prepare(self._web_request)

  async def send(self, msg: ServerMsgType) -> None:
    await self._ws.send_str(msg.data.model_dump_json())  # type: ignore

  async def __aiter__(self) -> AsyncIterator[TypedWSMessage[ClientMsgType]]:
    async for msg in self._ws:
      if msg.type == aiohttp.WSMsgType.TEXT:
        assert isinstance(msg.data, str)
        yield TypedWSMessage[ClientMsgType](
          type=msg.type,
          data=self._client_msg_loads(msg.data),
        )
      else:
        yield TypedWSMessage[ClientMsgType](
          type=msg.type,
          data=None,
        )
