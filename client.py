import aiohttp
import asyncio


async def create_user():
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8080/user/',
                                json={'username': 'user_3',
                                      'password': '1234'}) as response:
            print(await response.text())


async def user():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8080/user/') as response:
            print(await response.text())


async def delete_user():
    async with aiohttp.ClientSession() as session:
        async with session.delete('http://127.0.0.1:8080/user/2/') as response:
            print(await response.text())


async def update_user():
    async with aiohttp.ClientSession() as session:
        async with session.patch('http://127.0.0.1:8080/user/7/', json={'username': 'big '}) as response:
            print(await response.text())


async def create_ad():
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8080/ad/',
                                json={'title': 'ad-1',
                                      'description': '1234sdadsasdsad',
                                      'user': 'user_3'}) as response:
            print(await response.text())


async def ads():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8080/ad/1/') as response:
            print(await response.text())


async def delete_ad():
    async with aiohttp.ClientSession() as session:
        async with session.delete('http://127.0.0.1:8080/ad/3/') as response:
            print(await response.text())


async def update_ad():
    async with aiohttp.ClientSession() as session:
        async with session.patch('http://127.0.0.1:8080/ad/1/', json={'title': 'titletitle'}) as response:
            print(await response.text())


# asyncio.run(create_user())
# asyncio.run(user())
# asyncio.run(delete_user())
# asyncio.run(update_user())


# asyncio.run(create_ad())
# asyncio.run(ads())
# asyncio.run(delete_ad())
# asyncio.run(update_ad())
