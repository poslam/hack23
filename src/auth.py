from datetime import timedelta
from random import randint
import jwt
from jwt import decode
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash, generate_password_hash

from config import SECRET_AUTH
from database.database import get_session
from database.models import User
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from src.malfunc import time


auth_router = APIRouter(
    prefix="/auth"
)


async def type_required(types: list,  request: Request,
                        session: AsyncSession = Depends(get_session)):
    data = None
    try:
        data = await request.json()
        auth = data["token"]
        data = decode(auth, SECRET_AUTH, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="token is invalid")

    user = await session.get(User, data["id"])

    if user == None:
        raise HTTPException(status_code=400, detail="user not found")

    if types != []:
        if user.type.name not in types and user.type.name != "superadmin":
            raise HTTPException(status_code=400, detail="not allowed")

    return user


async def login_required(auth: Request,
                         session: AsyncSession = Depends(get_session)):
    return await type_required([], auth, session)


async def admin_required(auth: Request,
                         session: AsyncSession = Depends(get_session)):
    return await type_required(["admin"], auth, session)


@auth_router.post("/login")
async def login(request: Request,
                session: AsyncSession = Depends(get_session)):
    try:
        data = await request.json()

        num = data["num"]
        password = data["password"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
        
    stmt = select(User).where(User.num == num)
    user = (await session.execute(stmt)).first()

    if user != None:
        user = user[0]

    else:
        raise HTTPException(status_code=400, detail="user doesn't exist")

    if check_password_hash(user.password, password):
        token = jwt.encode(
            {"id": user.id, "exp": time() + timedelta(days=60)},
            SECRET_AUTH,
        )
        
        return {"token": token, "type": user.type.name}

    raise HTTPException(status_code=400, detail="wrong auth data")


@auth_router.post("/signup")
async def signup(request: Request,
                 session: AsyncSession = Depends(get_session)):
    try:
        data = await request.json()
        first_name = data["first_name"]
        second_name = data["second_name"]
        third_name = data["third_name"]
        password = data["password"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")

    num = randint(1000, 9999)
    
    user_num = (await session.execute(
        select(User).where(User.num == num)
    )).first()
    
    while (user_num != None):
        num = randint(0, 1000)
    
        user_num = (await session.execute(
            select(User).where(User.num == num)
        )).first()

    user = {
        "first_name": first_name,
        "second_name": second_name,
        "third_name": third_name,
        "num": num,
        "password": generate_password_hash(password),
    }

    stmt = insert(User).values(user)
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "successfully registered"}
    except Exception as e:
        print(e)
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")
