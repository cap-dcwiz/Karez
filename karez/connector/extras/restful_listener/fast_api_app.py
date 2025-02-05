from datetime import timedelta
from typing import Annotated, List

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from dateutil.parser import parse
from dateutil.tz import gettz
from loguru import logger

from .models import Token, TokenData, User, Point
from .utils import get_user, authenticate_user, create_access_token

secret_key = ""
algorithm = ""
fake_users_db = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str,  Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class FastAPIApp:
    def __init__(self, restful_listener):
        global secret_key, algorithm, fake_users_db
        self.app = FastAPI()
        self.setup_routes()
        self.restful_listener = restful_listener
        self._uuids = None
        self.config = restful_listener.config
        secret_key = self.config.secret_key
        algorithm = self.config.algorithm
        fake_users_db = self.get_fake_users_db()
        logger.add("restful_listener.log", rotation="200 MB")

    @property
    def uuids(self):
        if self._uuids is None:
            self._uuids = [key for key in self.restful_listener.reference["uuid_map"]]
        return self._uuids

    def validate_uuid(self, point):
        if point.name not in self.uuids:
            raise HTTPException(status_code=400, detail="Invalid uuid")

    def validate_timestamp(self, point):
        try:
            tz_infos = {k: gettz(v) for k, v in self.restful_listener.config.tz_infos.items()}
            parse(point.timestamp, tzinfos=tz_infos).timestamp()
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid timestamp")

    async def process_point(self, point):
        await self.restful_listener.postprocess_item(dict(point), publish=True, flush=True)

    def get_fake_users_db(self):
        return {
            self.config.username: {
                "username": self.config.username,
                "full_name": "STDCT",
                "email": "STDCT@STDCT.com",
                "hashed_password": self.config.bcrypt_hashed_password
            }
        }


    def setup_routes(self):

        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            body = await request.body()
            logger.info(f"Request: {request.method} {request.url} Body: {body.decode('utf-8')}")
            response = await call_next(request)
            logger.info(f"Response status: {response.status_code}")
            return response

        @self.app.post("/token")
        async def login_for_access_token(
            form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        ) -> Token:
            user = authenticate_user(self.get_fake_users_db(), form_data.username, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=self.config.access_token_expire_minutes)
            access_token = create_access_token(
                data={"sub": user.username}, secret_key=self.config.secret_key, algorithm=self.config.algorithm, expires_delta=access_token_expires
            )
            return Token(access_token=access_token, token_type="bearer")

        @self.app.get("/points")
        async def get_points(bearer=Depends(get_current_active_user)):
            return self.uuids

        @self.app.post("/insert_point")
        async def insert_point(point: Point, bearer = Depends(get_current_active_user)):
            self.validate_uuid(point)
            self.validate_timestamp(point)
            await self.process_point(point)
            return point

        @self.app.post("/insert_points")
        async def insert_points(points: List[Point], bearer = Depends(get_current_active_user)):
            for point in points:
                self.validate_uuid(point)
                self.validate_timestamp(point)
                await self.process_point(point)
            return points

    def create_app(self):
        return self.app
