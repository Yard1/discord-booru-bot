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

from booru_helpers import *
from enum import Enum
import random
import asyncio


class Booru:
    booru_type = None
    booru_url = None
    booru_api_url = None
    max_limit = 1000

    def __init__(self, url):
        self.booru_url = url

    async def _init(self):
        raise NotImplementedError()

    async def get_images_api(
        self,
        limit: int = 0,
        pid: int = 0,
        tags: list = None,
        cid: int = 0,
        api_id: int = 0,
        **kwargs,
    ) -> str:
        raise NotImplementedError()

    async def get_random_image(self, tags: list, limit: int = 0) -> str:
        raise NotImplementedError()

    async def get_best_image(self, tags: list) -> str:
        raise NotImplementedError()

    async def get_wilson_image(self, tags: list) -> str:
        return await self.get_best_image(tags)

    async def get_latest_image(self, tags: list) -> str:
        raise NotImplementedError()

    async def get_images_count(self, tags: list, limit: int = 0) -> int:
        raise NotImplementedError()

    async def get_image(self, **kwargs) -> str:
        json = await self.get_documents([], 1, **kwargs)
        return await self.get_image_url(json[0])

    async def get_image_url(self, image_object: dict) -> str:
        raise NotImplementedError()

    async def get_documents(self, tags: list, limit: int, sleep: int = 0,) -> list:
        raise NotImplementedError()


class Gelbooru(Booru):
    booru_type = "Gelbooru"
    booru_url = None
    booru_api_url = None
    max_limit = 1000

    async def _init(self):
        self.booru_api_url = (
            f"{self.booru_url}/index.php?page=dapi&s=post&q=index&json=1"
        )

    async def get_images_api(
        self,
        limit: int = 0,
        pid: int = 0,
        tags: list = None,
        cid: int = 0,
        api_id: int = 0,
        **kwargs,
    ) -> str:
        args = [f"{k}={v}" for k, v in kwargs.items()]
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
        return f"{self.booru_api_url}&{'&'.join(args)}"

    async def get_random_image(self, tags: list, limit: int = 0) -> str:
        if limit <= 1:
            limit = self.max_limit
        json = await self.get_documents(tags=tags, limit=limit)
        return await self.get_image_url(random.choice(json))

    async def get_best_image(self, tags: list) -> str:
        tags.append("sort:score")
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_latest_image(self, tags: list) -> str:
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_images_count(self, tags: list, limit: int = 0) -> int:
        if limit <= 1:
            limit = self.max_limit
        raise NotImplementedError()

    async def get_image_url(self, image_object: dict) -> str:
        if "file_url" in image_object:
            if (
                "sample_url" in image_object
                and "file_size" in image_object
                and int(image_object["file_size"]) > 5000000
            ):
                return image_object["sample_url"]
            return image_object["file_url"]

        url = f"{self.booru_url}/images/{image_object['directory']}/{image_object['image']}"
        return url

    async def get_documents(
        self, tags: list, limit: int, sleep: int = 0, **kwargs
    ) -> list:
        combined_js = []
        pid = 0
        if limit < 1:
            limit = 1
        while True:
            api_url = await self.get_images_api(limit, pid, tags, **kwargs)
            if not api_url:
                break
            print(f"Found API link: {api_url}")
            js = await fetch_js(api_url)
            combined_js.extend(js)
            if len(js) < self.max_limit:
                limit = 0
            else:
                limit -= len(js)
            pid += 1
            if limit > 0:
                await asyncio.sleep(sleep)
            else:
                break
        return combined_js


class Moebooru(Booru):
    booru_type = "Moebooru"
    booru_url = None
    booru_api_url = None
    max_limit = 1000

    async def _init(self):
        self.booru_api_url = f"{self.booru_url}/post.json"

    async def get_images_api(
        self,
        limit: int = 0,
        pid: int = 0,
        tags: list = None,
        cid: int = 0,
        api_id: int = 0,
        **kwargs,
    ) -> str:
        args = [f"{k}={v}" for k, v in kwargs.items()]
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
        return f"{self.booru_api_url}?{'&'.join(args)}"

    async def get_random_image(self, tags: list, limit: int = 0) -> str:
        if limit <= 1:
            limit = self.max_limit
        json = await self.get_documents(tags=tags, limit=limit)
        return await self.get_image_url(random.choice(json))

    async def get_best_image(self, tags: list, limit: int = 1) -> str:
        tags.append("order:score")
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_latest_image(self, tags: list, limit: int = 1) -> str:
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_images_count(self, tags: list, limit: int = 0) -> int:
        if limit <= 1:
            limit = self.max_limit
        raise NotImplementedError()

    async def get_image_url(self, image_object: dict) -> str:
        if "file_url" in image_object:
            if (
                "sample_url" in image_object
                and "file_size" in image_object
                and int(image_object["file_size"]) > 5000000
            ):
                url = image_object["sample_url"]
            else:
                url = image_object["file_url"]

        parse_result = urllib.parse.urlparse(url)
        if not (parse_result.scheme and parse_result.netloc):
            url = f"{self.booru_url}/{url}"
            parse_result = urllib.parse.urlparse(url)
            if not (parse_result.scheme and parse_result.netloc):
                url = f"{self.booru_url}/images/{image_object['directory']}/{image_object['image']}"
        return url

    async def get_documents(
        self, tags: list, limit: int, sleep: int = 0, **kwargs
    ) -> list:
        combined_js = []
        pid = 0
        if limit < 1:
            limit = 1
        while True:
            api_url = await self.get_images_api(limit, pid, tags, **kwargs)
            if not api_url:
                break
            print(f"Found API link: {api_url}")
            js = await fetch_js(api_url)
            combined_js.extend(js)
            if len(js) < self.max_limit:
                limit = 0
            else:
                limit -= len(js)
            pid += 1
            if limit > 0:
                await asyncio.sleep(sleep)
            else:
                break
        return combined_js


class E621(Moebooru):
    booru_type = "E621"
    booru_url = None
    booru_api_url = None
    max_limit = 1000

    async def _init(self):
        self.booru_api_url = f"{self.booru_url}/posts.json"

    async def get_random_image(self, tags: list, limit: int = 1) -> str:
        tags.append("order:random")
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_best_image(self, tags: list, limit: int = 1) -> str:
        tags.append("order:score")
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_latest_image(self, tags: list, limit: int = 1) -> str:
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_image_url(self, image_object: dict) -> str:
        if (
            "sample" in image_object
            and "size" in image_object["file"]
            and int(image_object["file"]["size"]) > 5000000
        ):
            return image_object["sample"]["url"]
        return image_object["file"]["url"]

    async def get_documents(
        self, tags: list, limit: int, sleep: int = 2, **kwargs
    ) -> list:
        combined_js = []
        pid = 0
        if limit < 1:
            limit = 1
        while True:
            api_url = await self.get_images_api(limit, pid, tags, **kwargs)
            if not api_url:
                break
            print(f"Found API link: {api_url}")
            js = await fetch_js(api_url)
            js = js["posts"]
            combined_js.extend(js)
            if len(js) < self.max_limit:
                limit = 0
            else:
                limit -= len(js)
            pid += 1
            if limit > 0:
                await asyncio.sleep(sleep)
            else:
                break
        return combined_js


class Danbooru(Moebooru):
    booru_type = "Danbooru"
    booru_url = None
    booru_api_url = None
    max_limit = 200

    async def _init(self):
        self.booru_api_url = f"{self.booru_url}/posts.json"

    async def get_images_api(
        self,
        limit: int = 0,
        pid: int = 0,
        tags: list = None,
        cid: int = 0,
        api_id: int = 0,
        **kwargs,
    ) -> str:
        args = [f"{k}={v}" for k, v in kwargs.items()]
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
        return f"{self.booru_api_url}?{'&'.join(args)}"

    async def get_random_image(self, tags: list, limit: int = 1) -> str:
        tags.append("order:random")
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_image_url(self, image_object: dict) -> str:
        if (
            "sample_url" in image_object
            and "file_size" in image_object
            and int(image_object["file_size"]) > 5000000
        ):
            return image_object["large_file_url"]
        return image_object["file_url"]

    async def get_documents(
        self, tags: list, limit: int, sleep: int = 1, **kwargs
    ) -> list:
        combined_js = []
        pid = 0
        if limit < 1:
            limit = 1
        while True:
            api_url = await self.get_images_api(limit, pid, tags, **kwargs)
            if not api_url:
                break
            print(f"Found API link: {api_url}")
            js = await fetch_js(api_url)
            combined_js.extend(js)
            if len(js) < self.max_limit:
                limit = 0
            else:
                limit -= len(js)
            pid += 1
            if limit > 0:
                await asyncio.sleep(sleep)
            else:
                break
        return combined_js


class Shimmie2(Danbooru):
    booru_type = "Shimmie2"
    booru_url = None
    booru_api_url = None
    max_limit = 100

    async def _init(self):
        self.booru_api_url = f"{self.booru_url}/api/danbooru/post/index.xml"

    async def get_random_image(self, tags: list, limit: int = 0) -> str:
        if limit <= 1:
            limit = self.max_limit
        json = await self.get_documents(tags=tags, limit=limit)
        return await self.get_image_url(random.choice(json))

    async def get_best_image(self, tags: list, limit: int = 1) -> str:
        tags.append("order:score_desc")
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_latest_image(self, tags: list, limit: int = 1) -> str:
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_image_url(self, image_object: dict) -> str:
        return image_object["@file_url"]

    async def get_documents(
        self, tags: list, limit: int, sleep: int = 0, **kwargs
    ) -> list:
        combined_js = []
        pid = 0
        if limit < 1:
            limit = 1
        while True:
            api_url = await self.get_images_api(limit, pid, tags, **kwargs)
            if not api_url:
                break
            print(f"Found API link: {api_url}")
            js = await fetch_xml(api_url)
            try:
                js = (
                    [js["posts"]["post"]]
                    if not isinstance(js["posts"]["post"], list)
                    else js["posts"]["post"]
                )
                combined_js.extend(js)
            except:
                return combined_js
            if len(js) < self.max_limit:
                limit = 0
            else:
                limit -= len(js)
            pid += 1
            if limit > 0:
                await asyncio.sleep(sleep)
            else:
                break
        return combined_js


# Derpibooru
class Philomena(Booru):
    booru_type = "Philomena"
    booru_url = None
    booru_api_url = None
    max_limit = 50

    class Filter(Enum):
        Everything = 56027

    async def _init(self):
        self.booru_api_url = f"{self.booru_url}/api/v1/json/search/images"

    async def get_images_api(
        self,
        limit: int = 0,
        pid: int = 0,
        tags: list = None,
        cid: int = 0,
        api_id: int = 0,
        sort: str = "",
        **kwargs,
    ) -> str:
        args = [f"{k}={v}" for k, v in kwargs.items()]
        args.append(f"filter_id={self.Filter.Everything.value}")
        if limit:
            limit = f"per_page={limit}"
            args.append(limit)
        if sort:
            sort = f"sf={sort}"
            args.append(sort)
        if tags:
            tags = f"q={'%2C'.join(tags)}"
            args.append(tags)
        return f"{self.booru_api_url}?{'&'.join(args)}"

    async def get_random_image(self, tags: list, limit: int = 1) -> str:
        json = await self.get_documents(tags=tags, limit=1, sort="random")
        return await self.get_image_url(json[0])

    async def get_best_image(self, tags: list, limit: int = 1) -> str:
        json = await self.get_documents(tags=tags, limit=1, sort="score")
        return await self.get_image_url(json[0])

    async def get_wilson_image(self, tags: list, limit: int = 1) -> str:
        json = await self.get_documents(tags=tags, limit=1, sort="wilson_score")
        return await self.get_image_url(json[0])

    async def get_latest_image(self, tags: list, limit: int = 1) -> str:
        json = await self.get_documents(tags=tags, limit=1)
        return await self.get_image_url(json[0])

    async def get_images_count(self, tags: list, limit: int = 0) -> int:
        raise NotImplementedError()

    async def get_image_url(self, image_object: dict) -> str:
        return image_object["view_url"]

    async def get_documents(
        self, tags: list, limit: int, sleep: int = 0, sort=None, **kwargs
    ) -> list:
        combined_js = []
        pid = 0
        if limit < 1:
            limit = 1
        while True:
            api_url = await self.get_images_api(limit, pid, tags, 0, 0, sort, **kwargs)
            if not api_url:
                break
            print(f"Found API link: {api_url}")
            js = await fetch_js(api_url)
            js = js["images"]
            combined_js.extend(js)
            if len(js) < self.max_limit:
                limit = 0
            else:
                limit -= len(js)
            pid += 1
            if limit > 0:
                await asyncio.sleep(sleep)
            else:
                break
        return combined_js


async def create_booru(booru_url: str) -> Booru:
    booru = None

    api_url = f"{booru_url}/index.php?page=dapi"
    if not booru and await check_if_url_works(api_url):
        booru = Gelbooru(booru_url)
    api_url = f"{booru_url}/posts.json"
    if not booru and await check_if_url_works(api_url):
        json = await fetch_js(api_url)
        if json:
            if "posts" in json:
                booru = E621(booru_url)
            else:
                booru = Danbooru(booru_url)
    api_url = f"{booru_url}/post.json"
    if not booru and await check_if_url_works(api_url):
        booru = Moebooru(booru_url)
    api_url = f"{booru_url}/api/v1/json/search/images"
    if not booru and await check_if_url_works(api_url):
        booru = Philomena(booru_url)
    api_url = f"{booru_url}/api/danbooru/post/index.xml"
    if not booru and await check_if_url_works(api_url):
        booru = Shimmie2(booru_url)
    if booru:
        await booru._init()
    return booru
