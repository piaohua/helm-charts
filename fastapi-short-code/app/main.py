from typing import Union

from fastapi import FastAPI, APIRouter, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from asgi_correlation_id import CorrelationIdMiddleware, CorrelationIdFilter, correlation_id
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from uvicorn.config import LOGGING_CONFIG

import mmh3
import random
import logging
import os
from . import snowflake

class URL(BaseModel):
    long_url: str
    short_url: str | None = None

def configure_logging():
    console_handler = logging.StreamHandler()
    console_handler.addFilter(CorrelationIdFilter())
    logging.basicConfig(
        handlers=[console_handler],
        level=logging.INFO,
        format="%(levelname)s log [%(correlation_id)s] %(name)s [%(pathname)s/%(funcName)s:%(lineno)d] %(message)s")

app = FastAPI(on_startup=[configure_logging])
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['X-Requested-With', 'X-Request-ID'],
    expose_headers=['X-Request-ID']
)
router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
    )

logger = logging.getLogger()
log_level=os.environ.get("LOGLEVEL", logging.DEBUG)
logger.setLevel(log_level)

LOGGING_CONFIG["handlers"]["access"]["filters"] = [CorrelationIdFilter()]
LOGGING_CONFIG["formatters"]["access"]["fmt"] = "%(levelname)s access [%(correlation_id)s] %(name)s %(message)s"

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return await http_exception_handler(
        request,
        HTTPException(
            500,
            'Internal server error',
            headers={'X-Request-ID': correlation_id.get() or ""}
        ))

@app.get("/")
async def read_root():
    logger.info("get test")
    return {"Hello": "World"}

@router.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    logger.info("item_id %d, q %s" % (item_id, q))
    return {"item_id": item_id, "q": q}

@router.get("/short/code")
async def short_code():
    hash = random.randint(1, ((1<<32)-1))
    code = to_base62(hash)
    logger.info("code %s, hash %s" % (code, hash))
    return {"code": code}

@router.post("/short/url")
async def short_url(url: URL):
    logger.info("url %s" % url)
    hash = mmh3.hash(url.long_url, signed=False) # returns a 32-bit unsigned int
    url.short_url = to_base62(hash)
    return url

sf = snowflake.generate(0, 0)

@router.post("/id")
async def snowflake_id():
    id = next(sf)
    return {"id": str(id)}

@router.post("/{id}/parse")
async def snowflake_id_parse(id: int):
    result = snowflake.parse(id)
    return result

app.include_router(router)

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def to_base62(hash: int):
    code = ''
    while hash > 0:
        code += BASE62[hash % 62]
        hash //= 62
    return code
