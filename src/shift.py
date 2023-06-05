'''
shift/view
shift/add
shift/edit
'''

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update, insert
from database.models import Shift, Task, User
from src.malfunc import time

from src.auth import admin_required, login_required
from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession


shift_router = APIRouter(
    prefix="/shift"
)

@shift_router.post("/view")
async def view(# user=Depends(login_required),
               session: AsyncSession = Depends(get_session)):
    stmt = (select(Shift.id.label("shift_id"),
                  Shift.user_id.label("user_id"),
                  Shift.date.label("date"),
                  (User.second_name + ' ' + 
                   User.first_name + ' ' +
                   User.third_name).label("user_name"),
                  Shift.shift_time.label("shift_time"))
            .join(User, User.id == Shift.user_id)
            .order_by(Shift.date))
    
    shifts = (await session.execute(stmt)).all()
    
    result = []
    
    for shift in shifts:
        shift = shift._mapping
        tasks = (await session.execute(
            select(Task.id, Task.value,
                   Task.begin, Task.end,
                   Task.status, Task.name)
            .where(shift.user_id == Task.user_id)
            .where(Task.begin <= shift.date)
            .where(Task.end >= shift.date)
        )).all()
        
        temp = []
        for task in tasks:
            task = task._mapping

            if task.end < time() and task.status.name == "active":
                stmt = update(Task).where(Task.id == task.id).values(status="inactive")
                
                try:
                    await session.execute(stmt)
                    await session.commit()
                except:
                    await session.rollback()
                    raise HTTPException(status_code=500, detail="smth gone wrong") 
        
            temp.append(task)
        
        result.append({"date": shift.date,
                       "shift_id": shift.shift_id,
                       "user_name": shift.user_name,
                       "shift_time": shift.shift_time,
                       "tasks": temp})
        
    return result


@shift_router.post("/add")
async def add(request: Request, # user=Depends(admin_required),
               session: AsyncSession = Depends(get_session)):
    try:
        data = await request.json()
        
        user_id = data["user_id"]
        date = datetime.strptime(data["date"], "%Y-%m-%d")
        shift_time = data["shift_time"]
        
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
    
    stmt = (select(Shift)
            .where(Shift.user_id == user_id)
            .where(Shift.date == date))
    
    shift = (await session.execute(stmt)).first()
    
    if shift != None:
        raise HTTPException(status_code=400, detail="shift already exist")
    
    shift = {
        "user_id": user_id,
        "date": date,
        "shift_time": shift_time
    }
    
    stmt = (insert(Shift)
            .values(shift))
    
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "shift add success"}
    except Exception as e:
        print(e)
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")
    

@shift_router.post("/edit")
async def edit(request: Request, #user=Depends(admin_required)
               session: AsyncSession = Depends(get_session)):
    try:
        data = await request.json()
        
        shift_id = data["shift_id"]
        user_id = data["user_id"]
        date = datetime.strptime(data["date"], "%Y-%m-%d")
        shift_time = data["shift_time"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
    
    shift = await session.get(Shift, shift_id)
    
    if shift == None:
        raise HTTPException(status_code=400, detail="shift not found")
    
    stmt = (select(Shift)
            .where(Shift.user_id == user_id)
            .where(Shift.date == date))
    
    shift = (await session.execute(stmt)).first()
    
    if shift != None:
        raise HTTPException(status_code=400, detail="shift already exist")
    
    shift = {
        "user_id": user_id,
        "date": date,
        "shift_time": shift_time
    }
    
    stmt = (update(Shift)
            .where(Shift.id == shift_id)
            .values(shift))
    
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "shift edit success"}
    except Exception as e:
        print(e)
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")