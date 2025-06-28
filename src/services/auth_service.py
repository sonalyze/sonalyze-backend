from bson import ObjectId
from fastapi import HTTPException
from typing import Annotated

from fastapi.params import Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from database.engine import DataContext, get_db

logger = logging.getLogger("uvicorn.info")
bearer_scheme = HTTPBearer()


async def get_token_header(credentials: Annotated[HTTPAuthorizationCredentials,  Security(bearer_scheme)],
                           data_context: Annotated[DataContext, Depends(get_db)]) -> str:
    """
    Tries to get a token from Bearer Authorization header.
    Validates the tokens existence in the database.
    """

    token = credentials.credentials

    user = await data_context.users.find_one_by_id(HttpObjectId(token, HTTPException(status_code=401, detail="Unauthorized")))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return token


class HttpObjectId(ObjectId):
    """
    Extension class of ObjectId.
    By default, throws http bad request exception if an object id is invalid.
    If given an optional exception, it will throw that instead.
    """
    def __init__(
            self,
            object_id: str,
            exception: HTTPException = HTTPException(status_code=400, detail="Bad Request - Invalid Id Provided")) -> None:
        if self.is_valid(object_id):
            super().__init__(object_id)
        else:
            raise exception