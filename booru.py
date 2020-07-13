import io
import aiohttp
import asyncio
import urllib.parse
import traceback
import json
import random
import sys

HEADERS = {"User-Agent": "BooruBot/1.0"}
E621_API = "https://e621.net/posts.json"

ERROR_MESSAGE = "Something went wrong! Please try again."


async def parse_command(booru: str, limit: int, tags: tuple, modifier: str) -> str:
    try:
        message = await do_booru(booru, tags, modifier=modifier, limit=limit,)
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
    booru = await get_api(booru_url)
    if not booru:
        return (combined_js, booru_url, None)
    booru_type = booru[1]
    booru_api = booru[0]
    sort = None
    max_limit = 1000
    if booru_type == "Derpibooru":
        max_limit = 50
    if limit <= 1 and modifier and not modifier == "None":
        limit = 1000
        if booru_type == "Derpibooru":
            limit = 50
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
        elif modifier == "Random" and booru_api == E621_API:
            tags.append("order:random")
            limit = 1

    while True:
        api_url = await get_api_url(
            booru_api, booru_type=booru_type, tags=tags, limit=limit, pid=pid, sort=sort
        )
        print(f"Found API link: {api_url}")
        if not api_url:
            break
        booru_url = api_url[1]
        booru_type = api_url[2]
        js = await fetch_js(api_url[0])
        if booru_type == "Derpibooru":
            js = js["images"]
        elif booru_api == E621_API:
            js = js["posts"]
        combined_js.extend(js)
        if len(js) < max_limit:
            limit = 0
        else:
            limit -= len(js)
        pid += 1
        if limit > 0:
            if booru_api == E621_API:
                await asyncio.sleep(2)
        else:
            break
    return (combined_js, booru_url, booru_type)


async def get_image_data(image_url: str) -> io.BytesIO:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(image_url) as r:
            if r.status != 200:
                return None
            data = io.BytesIO(await r.read())
            return data


async def get_image_url(booru: str, booru_type: str, image_object) -> str:
    if not image_object:
        return ""
    if "file" in image_object and "url" in image_object["file"]:
        if (
            "sample" in image_object
            and "size" in image_object["file"]
            and int(image_object["file"]["size"]) > 5000000
        ):
            return image_object["sample"]["url"]
        return image_object["file"]["url"]
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


async def get_api(booru_url: str) -> str:
    api_url = f"{booru_url}/index.php?page=dapi"
    if await check_if_url_works(api_url):
        return (api_url, "Gelbooru")
    api_url = f"{booru_url}/post.json"
    if await check_if_url_works(api_url):
        return (api_url, "Danbooru")
    api_url = f"{booru_url}/posts.json"
    if await check_if_url_works(api_url):
        return (api_url, "Danbooru")
    api_url = f"{booru_url}/api/v1/json/search/images"
    if await check_if_url_works(api_url):
        return (api_url, "Derpibooru")

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
        booru = await get_api(booru_url)
        if not booru:
            return None
        booru_url = booru_url[0]
        booru_type = booru[1]

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
    return f"{booru_url}&{'&'.join(args)}"


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
    return f"{booru_url}?{'&'.join(args)}"


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
    return f"{booru_url}?{'&'.join(args)}"
