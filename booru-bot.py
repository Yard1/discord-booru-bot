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
            print(
                'Responding (Guild: %s, Channel: %s) with "%s"'
                % (message.guild, message.channel.name, return_message)
            )
            await message.channel.send(return_message)


async def parse_command(command: discord.Message) -> str:
    message = ""
    try:
        if command.content.startswith("$booru"):
            modifier = None
            if command.content.startswith("$booru-best ") or command.content.startswith(
                "$booru-b "
            ):
                modifier = "Score"
            elif command.content.startswith(
                "$booru-wilson "
            ) or command.content.startswith("$booru-w "):
                modifier = "Wilson"
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
                    'User %s (ID: %s, Guild: %s, Channel: %s) made a command "%s"'
                    % (
                        command.author.name,
                        command.author.id,
                        command.guild,
                        command.channel.name,
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


async def fix_url(booru_url: str) -> str:
    parse_result = urllib.parse.urlparse(booru_url)

    if not (parse_result.scheme and parse_result.netloc):
        booru_url = f"https://{booru_url}"
        parse_result = urllib.parse.urlparse(booru_url)
        if not (parse_result.scheme and parse_result.netloc):
            return None
    return booru_url


async def do_booru(
    booru_url: str, tags: list, modifier: str = "", limit: int = 1
) -> str:
    tags = [tag.strip() for tag in tags]
    image_url = ""
    image = None
    booru_url = await fix_url(booru_url)
    try:
        js = await get_js_pages(booru_url, tags, limit, modifier)
        booru_type = js[2]
        booru_url = js[1]
        js = js[0]
    except:
        traceback.print_exc()
        return ERROR_MESSAGE
    if js:
        if modifier == "Random" and not booru_type == "Derpibooru":
            random.shuffle(js)
        elif modifier == "Count":
            image = len(js)
            return f"On <{booru_url}> there are {image} images matching tags {tags}"

        for image in js:
            image_url = await get_image_url(booru_url, booru_type, image)
            if await check_if_url_works(image_url):
                break

    if not booru_type:
        return_message = f"Website {booru_url} is unsupported!"
    else:
        return_message = "No pictures found!"

    if not image_url:
        if modifier == "Count":
            return_message = f"On <{booru_url}> there are 0 images matching tags {tags}"
    else:
        return_message = image_url

    return return_message


async def get_js_pages(booru_url, tags, limit, modifier=""):
    combined_js = []
    pid = 0
    if limit < 1:
        limit = 1
    booru_type = await get_api(booru_url)
    if not booru_type:
        return (combined_js, booru_url, None)
    sort = None
    if limit <= 1 and modifier and not modifier == "None":
        limit = 1000
        max_limit = 1000
        if booru_type == "Derpibooru":
            limit = 50
            max_limit = 50
            if modifier == "Random":
                sort = "random"
                limit = 1
            if modifier == "Score":
                sort = "score"
                limit = 1
            if modifier == "Wilson":
                sort = "wilson_score"
                limit = 1
        elif modifier == "Score" or modifier == "Wilson":
            limit = 1
            if booru_type == "Danbooru":
                tags.append("order:score")
            elif booru_type == "Gelbooru":
                tags.append("sort:score")
    while limit > 0:
        api_url = await get_api_url(
            booru_url, booru_type=booru_type, tags=tags, limit=limit, pid=pid, sort=sort
        )
        print(f"Found API link: {api_url}")
        if not api_url:
            break
        booru_url = api_url[1]
        booru_type = api_url[2]
        js = await fetch_js(api_url[0])
        if booru_type == "Derpibooru":
            js = js["images"]
        combined_js.extend(js)
        if len(js) < max_limit:
            limit = 0
        else:
            limit -= len(js)
        pid += 1
    return (combined_js, booru_url, booru_type)


async def get_image_data(image_url: str) -> io.BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as r:
            if r.status != 200:
                return None
            data = io.BytesIO(await r.read())
            return data


async def get_image_url(booru: str, booru_type: str, image_object) -> str:
    if not image_object:
        return ""
    if "file_url" in image_object:
        if (
            "sample_url" in image_object
            and "file_size" in image_object
            and int(image_object["file_size"]) > 5000000
        ):
            return image_object["sample_url"]
        return image_object["file_url"]
    if "view_url" in image_object:
        return image_object["view_url"]
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
                return r.status < 400
    except:
        return False


async def get_api(booru_url: str) -> str:
    if await check_if_url_works(f"{booru_url}/index.php?page=dapi"):
        return "Gelbooru"
    elif await check_if_url_works(f"{booru_url}/post.json"):
        return "Danbooru"
    elif await check_if_url_works(f"{booru_url}/api/v1/json/search/images"):
        return "Derpibooru"
    else:
        return None


async def get_api_url(
    booru_url,
    booru_type: str = "",
    limit: int = 0,
    pid: int = 0,
    tags: list = None,
    cid: int = 0,
    api_id: int = 0,
    sort: str = "",
) -> str:

    if not booru_type:
        booru_type = await get_api(booru_url)
        if not booru_type:
            return None

    if booru_type == "Gelbooru":
        api_url = await get_gelbooru_api_url(booru_url, limit, pid, tags, cid, api_id)
    elif booru_type == "Danbooru":
        api_url = await get_danbooru_api_url(booru_url, limit, pid, tags, cid, api_id)
    elif booru_type == "Derpibooru":
        api_url = await get_derpibooru_api_url(booru_url, limit, tags, sort)
    else:
        return None
    return (api_url, booru_url, booru_type)


async def get_gelbooru_api_url(
    booru_url,
    limit: int = 0,
    pid: int = 0,
    tags: list = None,
    cid: int = 0,
    api_id: int = 0,
) -> str:
    args = ["s=post", "q=index", "json=1"]
    if limit:
        limit = f"limit={limit}"
        args.append(limit)
    if pid:
        pid = f"pid={pid}"
        args.append(pid)
    if tags:
        tags = f"tags={'+'.join(tags)}"
        args.append(tags)
    if cid:
        cid = f"cid={cid}"
        args.append(cid)
    if api_id:
        api_id = f"id={api_id}"
        args.append(api_id)
    return f"{booru_url}/index.php?page=dapi&{'&'.join(args)}"


async def get_danbooru_api_url(
    booru_url,
    limit: int = 0,
    pid: int = 0,
    tags: list = None,
    cid: int = 0,
    api_id: int = 0,
) -> str:
    args = []
    if limit:
        limit = f"limit={limit}"
        args.append(limit)
    if pid:
        pid = f"page={pid}"
        args.append(pid)
    if tags:
        tags = f"tags={'+'.join(tags)}"
        args.append(tags)
    if cid:
        cid = f"cid={cid}"
        args.append(cid)
    if api_id:
        api_id = f"id={api_id}"
        args.append(api_id)
    return f"{booru_url}/post.json?{'&'.join(args)}"


async def get_derpibooru_api_url(
    booru_url, limit: int = 0, tags: list = None, sort: str = ""
) -> str:
    args = ["filter_id=56027"]  # everything
    if limit:
        limit = f"per_page={limit}"
        args.append(limit)
    if sort:
        sort = f"sf={sort}"
        args.append(sort)
    if tags:
        tags = f"q={'%2C'.join(tags)}"
        args.append(tags)
    return f"{booru_url}/api/v1/json/search/images?{'&'.join(args)}"


if __name__ == "__main__":
    CLIENT.run(str(sys.argv[1]))

