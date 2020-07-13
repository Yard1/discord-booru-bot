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
            elif command.content.startswith("$booru-count "):
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
                message = await do_booru(
                    command_message[1], command_message[2:], modifier
                )
    except:
        traceback.print_exc()
        message = ERROR_MESSAGE
    finally:
        return message


async def do_booru(booru, tags, modifier=None):
    tags = [tag.strip() for tag in tags]
    limit = 1
    if modifier and not modifier == "None":
        limit = 101
    api_url = await get_api_url(booru, tags=tags, limit=limit)
    if not api_url:
        return "Wrong booru address!"
    js = await fetch_js(api_url[0])
    booru = api_url[1]
    image_url = ""
    if js:
        if modifier == "Random":
            js = random.choice(js)
        elif modifier == "Best":
            js = sorted(js, reverse=True, key=lambda x: int(x["score"]))[0]
        elif modifier == "Count":
            js = len(js)
            return f"On {booru} there are {js} images matching tags {tags}"
        else:
            js = js[0]
        if js:
            image_url = f"{booru}/images/{js['directory']}/{js['image']}"
    return_message = None
    image_data = None
    if image_url:
        image_data = image_url

    if not image_data or not image_data[0]:
        image_data = "No pictures found!"
    return image_data


async def get_image_data(image_url: str) -> io.BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as r:
            if r.status != 200:
                return None
            data = io.BytesIO(await r.read())
            return data


async def fetch_js(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                text = await r.text()
                if text:
                    return json.loads(text)
    return None


async def get_api_url(
    booru,
    limit: str = "",
    pid: str = "",
    tags: list = None,
    cid: str = "",
    api_id: str = "",
) -> str:
    if limit:
        limit = f"&limit={limit}"
    if pid:
        pid = f"&pid={pid}"
    if tags:
        tags = f"&tags={'+'.join(tags)}"
    else:
        tags = ""
    if cid:
        cid = f"&cid={cid}"
    if api_id:
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

