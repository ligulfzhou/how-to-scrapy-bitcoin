import json
import asyncio
from aiohttp import web
from db import DB
from typing import NoReturn


conn = DB()

# loop = asyncio.get_event_loop()
# app = web.Application(loop=loop)
app = web.Application()


async def index(request: web.Request) -> web.StreamResponse:
    return web.Response(text="It works")


async def save(request: web.Request) -> web.StreamResponse:
    data = await request.json()
    if 'address' in data:
        conn.save_kp(data)
    elif 'mnemonic' in data:
        conn.save_mnemonic_path(data)
    return web.Response(text="saved!")


async def query(request: web.Request) -> web.StreamResponse:
    data = await request.json()
    res = {}
    if 'addresses' in data:
        for address in data['addresses']:
            res.update({
                address: conn.get_privkey_of_addr(address)
            })
    elif 'mnemonics' in data:
        for mnemonic in data['mnemonics']:
            res.update({
                mnemonic: conn.get_path_of_mnemonic(mnemonic)
            })

    return web.Response(text=json.dumps(res))


app.router.add_get("/", index)
app.router.add_post("/save", save)
app.router.add_post("/query", query)

web.run_app(app)
