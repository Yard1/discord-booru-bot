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
from booru_helpers import *
from booru_api import create_booru, Booru, Philomena, Gelbooru, E621, Moebooru

ERROR_MESSAGE = "Something went wrong, or the site is unsupported! Please try again."


async def parse_command(booru: str, limit: int, tags: tuple, modifier: str) -> str:
    try:
        message = await do_booru(booru, tags, modifier=modifier, limit=limit)
    except:
        traceback.print_exc()
        message = ERROR_MESSAGE
    finally:
        return message


async def do_booru(
    booru_url: str, tags: list, modifier: str = "", limit: int = 0
) -> str:
    tags = [tag.strip() for tag in tags]
    return_message = ""
    booru_url = await fix_url(booru_url)
    print(booru_url)
    try:
        booru = await create_booru(booru_url)
        print(f"{booru_url} classified as {booru.booru_type}")
        if modifier == "Random":
            return_message = await booru.get_random_image(tags, limit)
        elif modifier == "Score":
            return_message = await booru.get_best_image(tags)
        elif modifier == "Wilson":
            return_message = await booru.get_wilson_image(tags)
        else:
            return_message = await booru.get_latest_image(tags)
    except Exception as ex:
        if isinstance(ex, IndexError):
            return "No images found!"
        traceback.print_exc()
        return ERROR_MESSAGE

    if not return_message:
        return_message = "No images found, or booru not supported!"

    return return_message
