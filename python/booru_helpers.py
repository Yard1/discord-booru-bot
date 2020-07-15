# discord-booru-bot by Yard1
#
# MIT License
#
# Copyright (c) 2020 Antoni Baum (Yard1)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
import aiohttp
import asyncio
import urllib.parse
import traceback
import json
import random
import sys
import socket
import xmltodict

HEADERS = {"User-Agent": "discord-booru-bot/1.0"}

ERROR_MESSAGE = "Something went wrong, or the site is unsupported! Please try again."


async def is_int(text: str) -> bool:
    try:
        int(text)
        return True
    except:
        return False


async def fix_url(booru_url: str) -> str:
    parse_result = urllib.parse.urlparse(booru_url)
    if not (parse_result.scheme and parse_result.netloc):
        booru_url_https = f"https://{booru_url}"
        if await check_if_url_works(booru_url_https):
            return booru_url_https
        else:
            booru_url_http = f"http://{booru_url}"
            if await check_if_url_works(booru_url_http):
                return booru_url_http
    return booru_url


async def fetch_js(url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS) as session:
        async with session.get(url, ssl=False) as r:
            if r.status == 200:
                text = await r.text()
                if text:
                    return json.loads(text)
    return []


async def fetch_xml(url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS) as session:
        async with session.get(url, ssl=False) as r:
            if r.status == 200:
                text = await r.text()
                if text:
                    return xmltodict.parse(text, process_namespaces=True)
    return []


async def check_if_url_works(url: str, strict=False) -> bool:
    parse_result = urllib.parse.urlparse(url)
    if not (parse_result.scheme and parse_result.netloc):
        return False
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS) as session:
            async with session.head(url, ssl=False) as r:
                if strict:
                    return r.status == 200
                return r.status < 400
    except:
        return False
