from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

import mmh3
import random

class URL(BaseModel):
    long_url: str
    short_url: str | None = None

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/short/code")
async def short_code():
    hash = random.randint(1, ((1<<32)-1))
    code = to_base62(hash)
    return {"code": code}

@app.post("/short/url")
async def short_url(url: URL):
    hash = mmh3.hash(url.long_url, signed=False) # returns a 32-bit unsigned int
    url.short_url = to_base62(hash)
    return url

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
async def to_base62(hash: int):
    code = ''
    while hash > 0:
        code += BASE62[hash % 62]
        hash //= 62
    return code
