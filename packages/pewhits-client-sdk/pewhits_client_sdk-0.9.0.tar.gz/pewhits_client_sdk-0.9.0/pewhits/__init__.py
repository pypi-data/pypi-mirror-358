import os, sys, threading
from quattro import TaskGroup
from dataclasses import asdict
from aiohttp import ClientWebSocketResponse
from itertools import count
from typing import TYPE_CHECKING, Any, Callable, Literal, Protocol, TypeVar, Union, TypeVar, Protocol, Callable, Any 
import json
from cattrs.preconf.json import make_converter
from cattrs import structure
from asyncio import Queue
from typing import *
from .models import *

if TYPE_CHECKING:
    from attrs import AttrsInstance
else:

    class AttrsInstance(Protocol):
        pass

__all__ = [
    "PewHits",
    "PewHitsClient",
]

class PewHitsClient:
    """A Base class for PewHitsClient.
    Here all the WebSocket POST functions will be defined."""
    
    ws: ClientWebSocketResponse
    tg: TaskGroup
    _req_id = count()
    _req_id_registry: dict[str, Queue[Any]] = {}
        
    async def now_playing(self) -> NowPlayingRequest.NowPlayingResponse | Error:
        """Called when a current song is fetched.
        """
        resp = await do_req_resp(self, "now", NowPlayingRequest(), NowPlayingRequest.NowPlayingResponse)
        if isinstance(resp, Error):
            return resp
        return resp
    
    async def next_coming(self) -> NextComingRequest.NextComingResponse | Error:
        """Called when a next song is fetched.
        """
        resp = await do_req_resp(self, "next", NextComingRequest(), NextComingRequest.NextComingResponse)
        if isinstance(resp, Error):
            return resp
        return resp
    
    async def queue(self) -> QueueRequest.QueueResponse | Error:
        """Called when the queue is updated/fetched.
        """
        resp = await do_req_resp(self, "queue", QueueRequest(), QueueRequest.QueueResponse)
        if isinstance(resp, Error):
            return resp
        return resp

    async def blocklist(self) -> BlocklistRequest.BlocklistResponse | Error:
        """Called when the blocklist is requested.
        """
        resp = await do_req_resp(self, "blocklist", BlocklistRequest(), BlocklistRequest.BlocklistResponse)
        if isinstance(resp, Error):
            return resp
        return resp
    
    async def skip(self) -> SkipSongRequest.SkipSongResponse | Error:
        """Called when a song is skipped.
        """
        resp = await do_req_resp(self, "skip", SkipSongRequest(), SkipSongRequest.SkipSongResponse)
        if isinstance(resp, Error):
            return resp
        return resp
    
    async def unblock(self, index: int, app_name: str, is_moderator: bool) -> UnblockSongRequest.UnblockSongResponse | Error:
        """Called when a song is unblocked.
        """
        resp = await do_req_resp(self, "unblock", UnblockSongRequest(index, app_name, is_moderator), UnblockSongRequest.UnblockSongResponse)
        if isinstance(resp, Error):
            return resp
        return resp
    
    async def block(self, blocker: str, app_name: str, is_moderator: bool) -> BlockSongRequest.BlockSongResponse | Error:
        """Called when a song is blocked.
        """
        resp = await do_req_resp(self, "block", BlockSongRequest(blocker, app_name, is_moderator), BlockSongRequest.BlockSongResponse)
        if isinstance(resp, Error):
            return resp
        return resp
    
    async def remove(self, song_index: str, requester: str, app_name: str, is_moderator: bool) -> RemoveSongRequest.RemoveSongResponse | Error:
        """Called when a song is removed from the queue.
        """
        resp = await do_req_resp(self, "remove", RemoveSongRequest(song_index, requester, app_name, is_moderator), RemoveSongRequest.RemoveSongResponse)
        if isinstance(resp, Error):
            return resp
        return resp
    
    async def play(self, song_name: str, requester: str, app_name: str, ) -> PlaySongRequest.PlaySongResponse | Error:
        """Called when a song is play request made.
        """
        resp = await do_req_resp(self, "play", PlaySongRequest(song_name, requester, app_name), PlaySongRequest.PlaySongResponse)
        if isinstance(resp, Error):
            return resp
        return resp
    
    async def reloadall(self) -> ReloadAllRequest.ReloadAllResponse | Error:
        """Called when a song is play request made.
        """
        resp = await do_req_resp(self, "reloadall", ReloadAllRequest(), ReloadAllRequest.ReloadAllResponse)
        if isinstance(resp, Error):
            return resp
        return resp
    
class PewHits:
    """A Base class for PewHits.
    Here all the WebSocket GET functions will be defined."""
    
    pewhits: PewHitsClient
    
    async def before_start(self, tg: TaskGroup) -> None:
        """Called before the radio starts."""
        pass

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        """On a connection to the radio being established.
        """
        pass
    
    async def on_start_now_playing(self, now_playing: NowPlayingSong) -> None:
        """On a connection to the radio being established.
        Server sends the current playing song.
        """
        pass
    
    async def broadcast_now_playing(self, now_playing: NowPlayingSong) -> None:
        """When the song gets changed.
        Server sends the current playing song.
        """
        pass
    
class ResponseError(Exception):
    """An API response error."""

class _ClassWithId(AttrsInstance):
    rid: str | None
    
CID = TypeVar("CID", bound=_ClassWithId, covariant=True)


class _ReqWithId(AttrsInstance, Protocol[CID]):
    rid: str | None

    @property
    def Response(self) -> type[CID]:
        ...

async def do_req_resp(
    pw: PewHitsClient,
    action: str,
    req: _ReqWithId[CID],
    response_cls: Optional[Type[CID]] = None
) -> CID | Error:
    
    rid = str(next(pw._req_id))
    req.rid = rid
    pw._req_id_registry[rid] = (q := Queue[Any](maxsize=1))
    payload = {
        "action": action,
        "rid": rid,
        **converter.unstructure(req)
    }
    await pw.ws.send_str(json.dumps(payload))

    raw_response = await q.get()

    if isinstance(raw_response, dict) and (raw_response.get("type") == "error" or raw_response.get("code", 200) >= 400):
        return structure(raw_response, Error)

    # Prioritize provided response_cls, then fallback to req.Response
    response_type = response_cls or getattr(type(req), "Response", None)
    if response_type:
        return structure(raw_response, response_type)

    return raw_response  # fallback in case nothing matches

converter = make_converter()