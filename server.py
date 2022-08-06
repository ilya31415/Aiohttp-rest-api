from aiohttp import web
from gino import Gino

PG_DSN = 'postgres://aiohttp:1234@127.0.0.1:5432/aiohttp'





app = web.Application()

db = Gino()


async def init_orm(app):
    print('приложение стартовало')
    await db.set_bind(PG_DSN)
    yield
    await db.pop_bind().close()
    print('приложение закрывается')

async def test(response):
    return web.json_response(
        {'he': 'world'}
    )


app.router.add_route('GET', '/test/', test)
app.cleanup_ctx.append(init_orm)

web.run_app(app)
