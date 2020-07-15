# discord-booru-bot

Discord bot to get images from various image boorus. Will try to automatically determine which API is used.

## Usage

Run `python/booru_bot.py <DISCORDTOKEN>` from command line.

## Supported APIs

* Gelbooru
* Danbooru
* Shimmie2
* e621.net
* Derpibooru

## Commands
```
discord-booru-bot by Yard1

​No Category:
  booru        Get the latest image with tags.
  booru_best   Get the image with tags with highest Score.
  booru_random Get a random image with tags.
  booru_wilson Get the image with tags with highest Wilson Score. Defaults to booru_score if unsupported.
  help         Shows this message

Type $help command for more info on a command.
You can also type $help category for more info on a category.
```

## Author

Antoni Baum

## License

MIT
