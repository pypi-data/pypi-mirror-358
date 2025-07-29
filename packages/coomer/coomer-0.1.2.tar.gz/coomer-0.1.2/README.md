# Coomer

This package is Api client for coomer/kemono.

## Installing

```bash
pip install coomer
```

## Installing async version

```bash
pip install coomer[aiohttp]
```

## Getting started

### Client

To get posts from the creator:

```python
from coomer import Creator

creator = Creator(name="test")
posts = creator.get_posts()
for p in posts:
    print(f"{p.id}\tfiles:{len(p.files)}\t{p.title}")
```

### Changing domain

```python
parser = Parser(domain='kemono.su')
creator = Creator(name="test", parser=parser)
```


### Async Client

To get posts from the creator asynchronously:

```python
import asyncio
from coomer.asyncio import AsyncCreator

async def test():
    creator = Creator(name="test")
    posts = creator.get_posts()
    async for p in posts:
        print(f"{p.id}\tfiles:{len(p.files)}\t{p.title}")

asyncio.run(test())
```
