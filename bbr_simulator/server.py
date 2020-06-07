import os
import json
import aiohttp
import asyncio
from aiohttp import web, WSCloseCode


async def websocket_handler(request, simulation):
  ws = web.WebSocketResponse()
  await ws.prepare(request)

  await ws.send_json({
    "type": "constants",
    "payload": simulation.get_constants()
  })

  while not ws.closed:
    #try:
    #  msg = await ws.receive_json(timeout=1)
    #  print("waited and got", msg)
    #finally:
    #  print("got nothing?")

    try:
      await ws.send_json({
        "type": "state",
        "payload": simulation.get_state()
      })
    except RuntimeError:
      print("was closed")

    await asyncio.sleep(1.0/30)
  
  print("ws closed")

  return ws


async def start_server(simulation, host="127.0.0.1", port=1337):
  app = web.Application()
  web_root = os.path.join(os.path.dirname(__file__), "..", "web")

  app.add_routes([
    web.get("/ws", lambda request: websocket_handler(request, simulation)),
    web.get("/", lambda request: web.HTTPFound("/index.html")),
    web.static("/", web_root, append_version=True)
  ])

  runner = web.AppRunner(app)

  await runner.setup()
  site = web.TCPSite(runner, host, port)
  await site.start()
