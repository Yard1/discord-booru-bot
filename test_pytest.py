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


async def booru(booru, tags, sleep=0):
    return_message = await parse_command(booru, 1, tags, modifier="None")
    print(return_message)
    assert return_message.startswith("https://")
    await asyncio.sleep(sleep)

    return_message = await parse_command(booru, 50, tags, modifier="Random")
    print(return_message)
    assert return_message.startswith("https://")
    await asyncio.sleep(sleep)

    return_message = await parse_command(booru, 1, tags, modifier="Best")
    print(return_message)
    assert return_message.startswith("https://")
    await asyncio.sleep(sleep)

    return_message = await parse_command(booru, 1, tags, modifier="Wilson")
    print(return_message)
    assert return_message.startswith("https://")
    await asyncio.sleep(sleep)
