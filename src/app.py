'''
user/view
'''


from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from database.models import User
from src.auth import admin_required, auth_router
from src.dashboard import dashboard_router
from src.shift import shift_router
from src.task import task_router

app = FastAPI()

app.include_router(dashboard_router)
app.include_router(auth_router)
app.include_router(shift_router)
app.include_router(task_router)


@app.post("/user/view")
async def view(session: AsyncSession = Depends(get_session)):
    stmt = (select(User.id.label("user_id"),
                   (User.first_name + ' ' + 
                   User.second_name + ' ' +
                   User.third_name).label("user_name")))
    
    result = (await session.execute(stmt)).all()
    
    result = [x._mapping for x in result]
    
    return result

