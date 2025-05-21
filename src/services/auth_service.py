from bson import ObjectId
from fastapi import HTTPException
from typing import Annotated

from fastapi.params import Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from database.engine import DataContext, get_db

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()


async def get_token_header(credentials: Annotated[HTTPAuthorizationCredentials,  Security(bearer_scheme)],
                           data_context: Annotated[DataContext, Depends(get_db)]) -> str:
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = await data_context.users.find_one_by_id(ObjectId(token))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return token
