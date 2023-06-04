'''
task/today
task/add
task/confirm
task/unconfirm
task/edit
task/delete
'''


from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import insert, select, update, delete
from database.models import Task, User
from src.malfunc import time

from src.auth import login_required, admin_required
from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

task_router = APIRouter(
    prefix="/task"
)


@task_router.post("/today")
async def view_today(user=Depends(login_required),
                     session: AsyncSession=Depends(get_session)):
    tasks = (await session.execute(
            select(Task.id.label("task_id"), 
                   Task.value,
                   Task.begin,
                   Task.end,
                   Task.status,
                   Task.name.label("task_name"),
                   User.id.label("user_id"),
                   (User.first_name + ' ' + 
                   User.second_name + ' ' +
                   User.third_name).label("user_name"))
            .where(Task.begin <= time().date())
            .where(Task.end >= time().date())
            .join(User, Task.user_id == User.id)
        )).all()
    
    tasks = [task._mapping for task in tasks]
    return tasks


@task_router.post("/add")
async def add(request: Request, user=Depends(admin_required),
                     session: AsyncSession=Depends(get_session)):
    try:
        data = await request.json()
        
        user_id = data["user_id"]
        begin = datetime.strptime(data["begin"], "%Y-%m-%d")
        end = datetime.strptime(data["end"], "%Y-%m-%d")
        value = data["value"]
        name = data["name"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
    
    user = await session.get(User, user_id)
    
    if user == None:
        raise HTTPException(status_code=400, detail="user not found")
    
    task = (await session.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.begin == begin)
        .where(Task.end == end)
        .where(Task.value == value)
        .where(Task.name == name)
    )).first()
    
    if task != None:
        raise HTTPException(status_code=400, detail="task already exist")
    
    task = {
        "user_id": user_id,
        "begin": begin,
        "end": end,
        "value": value,
        "name": name,
        "status": "active"
    }
    
    stmt = insert(Task).values(task)
    
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "task add success"}
    except Exception as e:
        print(e)
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")
    
    
@task_router.post("/confirm")
async def confirm(request: Request, user=Depends(login_required),
                     session: AsyncSession=Depends(get_session)):
    try:
        data = await request.json()
        
        task_id = data["task_id"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
    
    task = await session.get(Task, task_id)
    
    if task == None:
        raise HTTPException(status_code=400, detail="task not found")
    
    if task.status.name == "inactive":
        raise HTTPException(status_code=400, detail="task status inactive")
    
    if task.status.name == "done":
        raise HTTPException(status_code=400, detail="task status done")
    
    stmt = (update(Task)
            .where(Task.id == task_id)
            .values(status="done"))
    
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "task confirm success"}
    except Exception as e:
        print(e)
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")
    

@task_router.post("/unconfirm")
async def unconfirm(request: Request, user=Depends(login_required),
                     session: AsyncSession=Depends(get_session)):
    try:
        data = await request.json()
        
        task_id = data["task_id"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
    
    task = await session.get(Task, task_id)
    
    if task == None:
        raise HTTPException(status_code=400, detail="task not found")
    
    if task.status.name == "inactive":
        raise HTTPException(status_code=400, detail="task status inactive")
    
    if task.status.name == "active":
        raise HTTPException(status_code=400, detail="task status active")

    stmt = (update(Task)
            .where(Task.id == task_id)
            .values(status="active"))
    
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "task confirm success"}
    except Exception as e:
        print(e)
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")
    

@task_router.post("/edit")
async def edit(request: Request, user=Depends(admin_required),
                     session: AsyncSession=Depends(get_session)):
    try:
        data = await request.json()
        
        task_id = data["task_id"]
        
        user_id = data["user_id"]
        begin = datetime.strptime(data["begin"], "%Y-%m-%d")
        end = datetime.strptime(data["end"], "%Y-%m-%d")
        value = data["value"]
        name = data["name"]
        
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
    
    task = await session.get(Task, task_id)
    
    if task == None:
        raise HTTPException(status_code=400, detail="task not found")
    
    if task.status.name == "inactive":
        raise HTTPException(status_code=400, detail="task status inactive")
    
    if task.status.name == "done":
        raise HTTPException(status_code=400, detail="task status done")

    if task.begin > task.end:
        raise HTTPException(status_code=400, detail="incorrect begin/end time")

    task_ins = {
        "user_id": user_id,
        "begin": begin,
        "end": end,
        "value": value,
        "name": name,
    }

    stmt = (update(Task)
            .where(Task.id == task_id)
            .values(task_ins))
    
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "task edit success"}
    except Exception as e:
        print(e)
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")
    
    
@task_router.post("/delete")
async def task_del(request: Request, user=Depends(admin_required),
                     session: AsyncSession=Depends(get_session)):
    try:
        data = await request.json()
        
        task_id = data["task_id"]
        
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
    
    task = await session.get(Task, task_id)
    
    if task == None:
        raise HTTPException(status_code=400, detail="task not found")
    
    stmt = (delete(Task)
            .where(Task.id == task_id))
    
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "task delete success"}
    except Exception as e:
        print(e)
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")