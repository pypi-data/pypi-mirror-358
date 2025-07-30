from .models import *
from .__init__ import *
from typing import *
from attrs import define
import asyncio
import websockets
import json
from aiohttp import *
from quattro import TaskGroup
from cattrs.preconf.json import make_converter
from cattrs import structure


WS_URL = "ws://eu-ro-01.wisp.uno:9364/ws"
KEEPALIVE_RATE: Final = 15
READ_TIMEOUT: Final = 20

@define
class ClientDefinition:
    client: PewHitsClient
    api_key: str
    
async def main(definition: ClientDefinition) -> None:
    async with TaskGroup() as tg:
        client = definition.client
        api_key = definition.api_key

        tg.create_task(client_runner(client, api_key))
        
async def client_runner(client: PewHits, api_key: str) -> None:
    async with TaskGroup() as tg:
        while True:
            try:
                await client.before_start(client, tg)
                async with ClientSession() as session:
                    async with session.ws_connect(WS_URL) as ws:
                        chat = PewHitsClient()
                        chat.ws = ws
                        chat.tg = tg
                        client.pewhits = chat

                        # Send API key
                        await ws.send_json({"api_key": api_key})
                        print("🔐 Authenticated with API Key.")

                        async def send_keepalive():
                            while True:
                                await asyncio.sleep(KEEPALIVE_RATE)
                                try:
                                    await ws.send_json({"action": "KeepAliveRequest"})
                                except Exception as e:
                                    print(f"💔 Keepalive failed: {e}")
                                    return

                        async def unified_receive_loop():
                            try:
                                async for msg in ws:
                                    if msg.type == WSMsgType.TEXT:
                                        data = msg.json()
                                        rid = data.get("rid")

                                        if rid and rid in chat._req_id_registry:
                                            await chat._req_id_registry[rid].put(data)
                                        else:
                                            # This is likely a notification/broadcast message
                                            action = data.get("action")
                                            if data.get("type") == "notification":
                                                if action == "on_start":
                                                    payload = data.get("session_metadata") or {}
                                                    session_metadata = structure(payload, SessionMetadata)
                                                    await client.on_start(client, session_metadata)
                                                elif action == "now_playing":
                                                    payload = data.get("data") or {}
                                                    now_playing = structure(payload, NowPlayingSong)
                                                    await client.on_start_now_playing(client, now_playing)
                                                elif action == "broadcast_now_playing":
                                                    payload = data.get("song") or {}
                                                    brd_now_playing = structure(payload, NowPlayingSong)
                                                    await client.broadcast_now_playing(client, brd_now_playing)
                                                elif action == "KeepAliveResponse":
                                                    pass
                                            else:
                                                print("🔔 Untracked/broadcast message:", data)

                                    elif msg.type == WSMsgType.CLOSE:
                                        print("🚪 Server closed the connection.")
                                        return
                                    elif msg.type == WSMsgType.ERROR:
                                        print("💥 Error in WS message.")
                                        return
                            except Exception as e:
                                print(f"💔 Listening error: {e}")
                                return

                        async with asyncio.TaskGroup() as tg:
                            tg.create_task(send_keepalive())
                            tg.create_task(unified_receive_loop())
                            
            except (WSServerHandshakeError, ClientConnectorError) as e:
                print(f"🚫 Connection error: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"❗ Unexpected error: {e}")
                await asyncio.sleep(5)