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

from booru import parse_command
import asyncio
import pytest


@pytest.mark.asyncio
async def test_derpibooru():
    await booru("derpibooru.org", ("pony", "female"))


@pytest.mark.asyncio
async def test_gelbooru():
    await booru("gelbooru.com", ("safe", "1girl"))


@pytest.mark.asyncio
async def test_yandere():
    await booru("yande.re", ("deru06", "fate/grand_order"))


@pytest.mark.asyncio
async def test_e621():
    await booru("e621.net", ("anthro", "female"), 2)


@pytest.mark.asyncio
async def test_danbooru():
    await booru("danbooru.donmai.us", ["yuri"], 1)

@pytest.mark.asyncio
async def test_colonize():
    await booru("colonize.us.to", ["blush", "breasts"], 1)

@pytest.mark.asyncio
async def test_paheal():
    await booru("rule34.paheal.net", ["yuri", "Doki_Doki_Literature_Club"], 1)

async def booru(booru, tags, sleep=0):
    return_message = await parse_command(booru, 1, tags, modifier="None")
    print(return_message)
    assert return_message.startswith("http")
    await asyncio.sleep(sleep)

    return_message = await parse_command(booru, 0, tags, modifier="Random")
    print(return_message)
    assert return_message.startswith("http")
    await asyncio.sleep(sleep)

    return_message = await parse_command(booru, 1, tags, modifier="Best")
    print(return_message)
    assert return_message.startswith("http")
    await asyncio.sleep(sleep)

    return_message = await parse_command(booru, 1, tags, modifier="Wilson")
    print(return_message)
    assert return_message.startswith("http")
    await asyncio.sleep(sleep)
