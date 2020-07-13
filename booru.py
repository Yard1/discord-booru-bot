import io
import aiohttp
import asyncio
import urllib.parse
import traceback
import json
import random
import sys
from booru_helpers import *
from booru_api import create_booru, Booru, Deribooru, Gelbooru, E621, Moebooru

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
