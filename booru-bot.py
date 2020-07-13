import discord
import io
import aiohttp
import asyncio
import urllib.parse
import traceback
import json
import random
import sys

CLIENT = discord.Client()

ERROR_MESSAGE = "Something went wrong! Please try again."


@CLIENT.event
async def on_ready():
    print("We have logged in as {0.user}".format(CLIENT))


@CLIENT.event
async def on_message(message: discord.Message):
    if message.author == CLIENT.user:
        return

    return_message = await parse_command(message)
    print(return_message)

    if return_message:
        if isinstance(return_message, str):
            await message.channel.send(return_message)


async def parse_command(command: discord.Message) -> str:
    message = ""
    try:
        if command.content.startswith("$booru"):
            modifier = None
            if command.content.startswith("$booru-best ") or command.content.startswith(
                "$booru-b "
            ):
                modifier = "Best"
            elif command.content.startswith(
                "$booru-random "
            ) or command.content.startswith("$booru-r "):
                modifier = "Random"
            elif command.content.startswith(
                "$booru-count "
            ) or command.content.startswith("$booru-c "):
                modifier = "Count"
            elif command.content.startswith("$booru "):
                modifier = "None"
            if modifier:
                print(
                    "User %s (ID: %s, Guild: %s) made a command %s"
                    % (
                        command.author.name,
                        command.author.id,
                        command.guild,
                        command.content,
                    )
                )
                command_message = command.content.strip().split()
                if await (is_int(command_message[1])):
                    message = await do_booru(
                        command_message[2],
                        command_message[3:],
                        modifier=modifier,
                        limit=int(command_message[1]),
                    )
                else:
                    message = await do_booru(
                        command_message[1], command_message[2:], modifier=modifier
                    )
    except:
        traceback.print_exc()
        message = ERROR_MESSAGE
    finally:
        return message


async def is_int(text: str) -> bool:
    try:
        int(text)
        return True
    except:
        return False


async def do_booru(booru, tags, modifier=None, limit=1):
    tags = [tag.strip() for tag in tags]
    if limit < 1:
        limit = 1
    if limit <= 1 and modifier and not modifier == "None":
        limit = 1000
    image_url = ""
    image = None
    try:
        js = await get_js_pages(booru, tags, limit)
        booru = js[1]
        js = js[0]
    except:
        traceback.print_exc()
    if js:
        print(len(js))
        if modifier == "Random":
            random.shuffle(js)
        elif modifier == "Best":
            js = sorted(
                js, reverse=True, key=lambda x: int(x["score"]) if x["score"] else 0
            )
        elif modifier == "Count":
            image = len(js)
            return f"On <{booru}> there are {image} images matching tags {tags}"

        for image in js:
            image_url = await get_image_url(booru, image)
            if await check_if_url_works(image_url):
                break

    return_message = "No pictures found!"
    if not image_url:
        if modifier == "Count":
            return_message = f"On <{booru}> there are 0 images matching tags {tags}"
    else:
        return_message = image_url

    return return_message


async def get_js_pages(booru, tags, limit):
    combined_js = []
    pid = 0
    while limit > 0:
        print(limit, len(combined_js))
        api_url = await get_api_url(booru, tags=tags, limit=limit, pid=pid)
        print(api_url)
        if not api_url:
            break
        js = await fetch_js(api_url[0])
        booru = api_url[1]
        combined_js.extend(js)
        if len(js) < 1000:
            limit = 0
        else:
            limit -= len(js)
        pid += 1
    return (combined_js, booru)


async def get_image_data(image_url: str) -> io.BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as r:
            if r.status != 200:
                return None
            data = io.BytesIO(await r.read())
            return data


async def get_image_url(booru, image_object) -> str:
    if not image_object:
        return ""
    try:
        url = f"{booru}/images/{image_object['directory']}/{image_object['image']}"
        return url
    except:
        return ""


async def fetch_js(url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
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
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head(url) as r:
                return r.status == 200
    except:
        return False


async def get_api_url(
    booru,
    limit: int = 0,
    pid: int = 0,
    tags: list = None,
    cid: int = 0,
    api_id: int = 0,
) -> str:
    if limit or limit == 0:
        limit = f"&limit={limit}"
    if pid or pid == 0:
        pid = f"&pid={pid}"
    if tags:
        tags = f"&tags={'+'.join(tags)}"
    else:
        tags = ""
    if cid or cid == 0:
        cid = f"&cid={cid}"
    if api_id or api_id == 0:
        api_id = f"&id={api_id}"

    parse_result = urllib.parse.urlparse(booru)

    if not (parse_result.scheme and parse_result.netloc):
        booru = f"https://{booru}"
        parse_result = urllib.parse.urlparse(booru)
        if not (parse_result.scheme and parse_result.netloc):
            return None
    return (
        f"{booru}/index.php?page=dapi&s=post&q=index&json=1{limit}{pid}{tags}{cid}{api_id}",
        booru,
    )


if __name__ == "__main__":
    CLIENT.run(str(sys.argv[1]))

