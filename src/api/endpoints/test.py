from fastapi import APIRouter, Depends
from sqlmodel import select, Session

from database.engine import get_session
from database.schemas import Test

router = APIRouter()

@router.get("/", tags=["test"])
async def read_test(session: Session = Depends(get_session)) -> Test | None:
    statement = select(Test).where(Test.id == 1)
    results = session.exec(statement)
    test = results.first()
    return test