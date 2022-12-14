import json
from datetime import datetime
from aiohttp import web
from gino import Gino
from asyncpg.exceptions import UniqueViolationError

PG_DSN = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    host="localhost",
    port=5433,
    user="aio",
    password=1234,
    database="qwe",
)

app = web.Application()
db = Gino()


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    __idx1 = db.Index('app_users_username', 'username', unique=True)


class AdModel(db.Model):
    __tablename__ = 'ads'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.now())
    user = db.Column(db.String, nullable=False)

    user_fk = db.ForeignKeyConstraint(['user'], ['users.username'])


class HTTPException(web.HTTPClientError):

    def __init__(self, *args, error='', **kwargs):
        kwargs['text'] = json.dumps({'error': error})
        super().__init__(*args, **kwargs, content_type='application/json')


class BadRequest(HTTPException):
    status_code = 400


class NotFound(HTTPException):
    status_code = 404


class UserView(web.View):

    async def get(self):

        user_id = self.request.match_info.get('user_id', None)
        if user_id is not None:
            user = await UserModel.get(int(user_id))
            if user is None:
                raise NotFound(error='user does not exist')
            return web.json_response(
                {'user_id': user.id,
                 'username': user.username,
                 'password': user.password}
            )
        all_users = await db.all(UserModel.query)
        response = [{'id': i.id, 'name': i.username, 'password': i.password} for i in all_users]

        return web.json_response(response)

    async def post(self):
        user_data = await self.request.json()
        try:
            new_user = await UserModel.create(**user_data)
        except UniqueViolationError:
            raise BadRequest(error='User already exists')
        return web.json_response(
            {'user_id': new_user.id,
             'username': new_user.username,
             'password': new_user.password}
        )

    async def delete(self):

        user_id = self.request.match_info.get('user_id', None)
        if user_id is not None:
            user = await UserModel.get(int(user_id))
            if user is None:
                raise NotFound(error='user does not exist')
            await user.delete()
            return web.json_response(
                {'user_id': user.id,
                 'username': user.username,
                 'password': user.password}
            )
        raise NotFound(error='user does not exist')

    async def patch(self):
        user_id = self.request.match_info.get('user_id', None)
        if user_id is not None:
            user = await UserModel.get(int(user_id))
            if user is None:
                raise NotFound(error='user does not exist')
            user_data = await self.request.json()
            update_user = await user.update(**user_data).apply()
            return web.json_response(
                {'user_id': user.id,
                 'username': user.username,
                 'password': user.password,
                 }
            )
        raise NotFound(error='user does not exist')


class AdView(web.View):

    async def get(self):
        ad_id = self.request.match_info.get('ad_id', None)
        if ad_id is not None:
            ad = await AdModel.get(int(ad_id))
            if ad is None:
                raise NotFound(error='ad does not exist')
            return web.json_response(
                {'ad_id': ad.id,
                 'title': ad.title,
                 'description': ad.description,
                 'user_name': ad.user,
                 'create_date': ad.create_date.strftime('%d.%b.%Y T %H:%M:%S')}
            )
        all_ad = await db.all(AdModel.query)
        response = [{'ad_id': i.id,
                     'title': i.title,
                     'description': i.description,
                     'user_name': i.user,
                     'create_date': i.create_date.strftime('%d.%b.%Y T %H:%M:%S')}
                    for i in all_ad]

        return web.json_response(response)

    async def post(self):
        ad_data = await self.request.json()
        user_name = ad_data.get('user', None)
        try:

            user = await UserModel.query.where(UserModel.username == user_name).gino.first()
            if user is not None:
                new_ad = await AdModel.create(**ad_data)
            else:
                raise BadRequest(error='there is no user with this name')
        except UniqueViolationError:
            raise BadRequest(error='Ad already exists')
        return web.json_response(
            {'ad_id': new_ad.id,
             'title': new_ad.title,
             'description': new_ad.description,
             'user_name': new_ad.user,
             'create_date': new_ad.create_date.strftime('%d.%b.%Y T %H:%M:%S')}
        )

    async def patch(self):
        ad_id = self.request.match_info.get('ad_id', None)

        if ad_id is not None:
            ad = await AdModel.get(int(ad_id))
            if ad is None:
                raise NotFound(error='ad does not exist')
            ad_data = await self.request.json()
            update_ad = await ad.update(**ad_data).apply()
            return web.json_response(
                {'ad_id': ad.id,
                 'title': ad.title,
                 'description': ad.description,
                 'user_name': ad.user,
                 'create_date': ad.create_date.strftime('%d.%b.%Y T %H:%M:%S')}
            )
        raise NotFound(error='ad does not exist')

    async def delete(self):
        ad_id = self.request.match_info.get('ad_id', None)

        if ad_id is not None:
            ad = await AdModel.get(int(ad_id))
            if ad is None:
                raise NotFound(error='ad does not exist')
            status = await ad.delete()
            return web.json_response(
                {'status': status,
                 'ad_id': ad.id,
                 'title': ad.title,
                 'description': ad.description,
                 'user_name': ad.user,
                 'create_date': ad.create_date.strftime('%d.%b.%Y T %H:%M:%S')}
            )
        raise NotFound(error='ad does not exist')


async def init_orm(app):
    print('???????????????????? ????????????????????')
    await db.set_bind(PG_DSN)
    await db.gino.create_all()
    yield
    await db.pop_bind().close()
    print('???????????????????? ??????????????????????')


async def test(response):
    return web.json_response(
        {'he': 'world'}
    )


app.router.add_route('GET', '/test/', test)
app.router.add_route('GET', '/user/{user_id:\d+}/', UserView)
app.router.add_route('GET', '/user/', UserView)
app.router.add_route('DELETE', '/user/{user_id:\d+}/', UserView)
app.router.add_route('PATCH', '/user/{user_id:\d+}/', UserView)
app.router.add_route('POST', '/user/', UserView)

app.router.add_route('GET', '/ad/', AdView)
app.router.add_route('GET', '/ad/{ad_id:\d+}/', AdView)
app.router.add_route('PATCH', '/ad/{ad_id:\d+}/', AdView)
app.router.add_route('DELETE', '/ad/{ad_id:\d+}/', AdView)
app.router.add_route('POST', '/ad/', AdView)

app.cleanup_ctx.append(init_orm)

web.run_app(app)
