import io
import aiohttp
import asyncio
import urllib.parse
import traceback
import json
import random
import sys

HEADERS = {"User-Agent": "BooruBot/1.0"}

ERROR_MESSAGE = "Something went wrong! Please try again."


async def is_int(text: str) -> bool:
    try:
        int(text)
        return True
    except:
        return False


async def fix_url(booru_url: str) -> str:
    parse_result = urllib.parse.urlparse(booru_url)

    if not (parse_result.scheme and parse_result.netloc):
        booru_url = f"https://{booru_url}"
        parse_result = urllib.parse.urlparse(booru_url)
        if not (parse_result.scheme and parse_result.netloc):
            return None
    return booru_url


async def fetch_js(url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS) as session:
        async with session.get(url) as r:
            if r.status == 200:
                text = await r.text()
                if text:
                    return json.loads(text)
    return []


async def check_if_url_works(url: str) -> bool:
    parse_result = urllib.parse.urlparse(url)
    if not (parse_result.scheme and parse_result.netloc):
        return False
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS) as session:
            async with session.head(url) as r:
                return r.status < 400
    except:
        return False
