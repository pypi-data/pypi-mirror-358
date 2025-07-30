# PGram
###### Blazingly fast start async telegram bot on top of the aiogram and tortoise-orm with postgres channels

### Install
```sh
pip install PGram
```

### Minimal code for running
```python
from asyncio import run
from PGram import Bot

bot = Bot("bot:token")
run(bot.start())
```
