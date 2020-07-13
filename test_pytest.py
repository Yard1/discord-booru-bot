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


async def booru(booru, tags, sleep=0):
    return_message = await parse_command(booru, 1, tags, modifier="None")
    assert return_message.startswith("https://")
    await asyncio.sleep(sleep)

    return_message = await parse_command(booru, 50, tags, modifier="Random")
    assert return_message.startswith("https://")
    await asyncio.sleep(sleep)

    return_message = await parse_command(booru, 1, tags, modifier="Best")
    assert return_message.startswith("https://")
    await asyncio.sleep(sleep)

    return_message = await parse_command(booru, 1, tags, modifier="Wilson")
    assert return_message.startswith("https://")
    await asyncio.sleep(sleep)
