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

import discord
import sys
from discord.ext import commands
from booru import parse_command
import typing

bot = commands.Bot(
    command_prefix="$", description="discord-booru-bot by Yard1", activity=discord.Game("$help")
)


@bot.listen()
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.command()
async def booru(ctx, booru: str, *tags: str):
    """Get the latest image with tags."""
    print(
        'User %s (ID: %s, Guild: %s, Channel: %s) made a command "%s"'
        % (
            ctx.message.author.name,
            ctx.message.author.id,
            ctx.message.guild,
            ctx.message.channel.name,
            ctx.message.content,
        )
    )
    return_message = await parse_command(booru, 1, tags, "None")
    await ctx.send(return_message)


@bot.command()
async def booru_best(ctx, booru: str, *tags: str):
    """Get the image with tags with highest Score."""
    print(
        'User %s (ID: %s, Guild: %s, Channel: %s) made a command "%s"'
        % (
            ctx.message.author.name,
            ctx.message.author.id,
            ctx.message.guild,
            ctx.message.channel.name,
            ctx.message.content,
        )
    )
    return_message = await parse_command(booru, 1, tags, "Score")
    print(
        'Sending (ID: %s, Guild: %s, Channel: %s) "%s"'
        % (
            ctx.message.author.id,
            ctx.message.guild,
            ctx.message.channel.name,
            return_message,
        )
    )
    await ctx.send(return_message)


@bot.command()
async def booru_random(ctx, booru: str, limit: typing.Optional[int] = 1, *tags: str):
    """Get a random image with tags."""
    print(
        'User %s (ID: %s, Guild: %s, Channel: %s) made a command "%s"'
        % (
            ctx.message.author.name,
            ctx.message.author.id,
            ctx.message.guild,
            ctx.message.channel.name,
            ctx.message.content,
        )
    )
    return_message = await parse_command(booru, limit, tags, "Random")
    print(
        'Sending (ID: %s, Guild: %s, Channel: %s) "%s"'
        % (
            ctx.message.author.id,
            ctx.message.guild,
            ctx.message.channel.name,
            return_message,
        )
    )
    await ctx.send(return_message)


@bot.command()
async def booru_wilson(ctx, booru: str, *tags: str):
    """Get the image with tags with highest Wilson Score. Defaults to booru_score if unsupported."""
    print(
        'User %s (ID: %s, Guild: %s, Channel: %s) made a command "%s"'
        % (
            ctx.message.author.name,
            ctx.message.author.id,
            ctx.message.guild,
            ctx.message.channel.name,
            ctx.message.content,
        )
    )
    return_message = await parse_command(booru, 1, tags, "Wilson")
    print(
        'Sending (ID: %s, Guild: %s, Channel: %s) "%s"'
        % (
            ctx.message.author.id,
            ctx.message.guild,
            ctx.message.channel.name,
            return_message,
        )
    )
    await ctx.send(return_message)


# @bot.command()
# async def booru_count(ctx, booru: str, limit: typing.Optional[int] = 1, *tags: str):
#     print(
#         'User %s (ID: %s, Guild: %s, Channel: %s) made a command "%s"'
#         % (
#             ctx.message.author.name,
#             ctx.message.author.id,
#             ctx.message.guild,
#             ctx.message.channel.name,
#             ctx.message.content,
#         )
#     )
#     return_message = await parse_command(booru, limit, tags, "Count")
#     print(
#         'Sending (ID: %s, Guild: %s, Channel: %s) "%s"'
#         % (
#             ctx.message.author.id,
#             ctx.message.guild,
#             ctx.message.channel.name,
#             return_message
#         )
#     )
#     await ctx.send(return_message)


bot.run(str(sys.argv[1]))
