from fastapi.params import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()


async def get_token_header(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> str:
    token = credentials.credentials
    # TODO validate token
    return token
