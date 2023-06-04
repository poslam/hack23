from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import insert, select
from src.malfunc import time

from src.auth import login_required
from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Component, Param, Product, Receipt


dashboard_router = APIRouter(
    prefix="/dashboard"
)


@dashboard_router.post("/view")
async def view(#user=Depends(login_required),
               session: AsyncSession = Depends(get_session)):
    stmt = (select(Product.id.label("product_id"),
                  Product.name.label("product_name"),
                  Receipt.id.label("receipt_id"),
                  Receipt.out_weight.label("receipt_out_weight"))
            .join(Receipt, Receipt.product_id == Product.id))
    
    products = (await session.execute(stmt)).all()
    
    result = []
    
    for product in products:
        product = dict(product._mapping)
        
        components = (await session.execute(
            select(Component.id.label("component_id"),
                   Component.name.label("component_name"),
                   Component.weight.label("component_weight"))
            .where(Component.receipt_id == product["receipt_id"])
        )).all()
        
        components = [component._mapping for component in components]
        
        params = (await session.execute(
            select(Param.id.label("param_id"),
                   Param.name.label("param_name"),
                   Param.value.label("param_value"))
            .where(Param.receipt_id == product["receipt_id"])
        )).all()
        
        params = [param._mapping for param in params]
        
        result.append(product | {"components": components} | {"params": params})
        
    return result
        
        
@dashboard_router.post("/add_product")
async def add(request: Request, #user=Depends(admin_required),
               session: AsyncSession = Depends(get_session)):
    try:
        data = await request.json()
        
        name = data["name"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
    
    product = (await session.execute(select(Product)
               .where(Product.name == name))).first()
    
    if product != None:
        raise HTTPException(status_code=400, detail="product already exist")
    
    prod_ins = {
        "name": name
    }
    
    stmt = insert(Product).values(prod_ins)
    
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "product add success"}
    except:
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")
        

@dashboard_router.post("/add_receipt")
async def add(request: Request, #user=Depends(admin_required),
               session: AsyncSession = Depends(get_session)):
    try:
        data = await request.json()
        
        product_id = data["product_id"]
        out_weight = data["out_weight"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")

    receipt = (await session.execute(select(Receipt)
               .where(Receipt.product_id == product_id)
               .where(Receipt.out_weight == out_weight)
    )).first()    
    
    if receipt != None:
        raise HTTPException(status_code=400, detail="receipt already exist")
    
    product = await session.get(Product, product_id)
    
    if product == None:
        raise HTTPException(status_code=400, detail="product not found")
    
    receipt_ins = {
        "product_id": product_id,
         "out_weight": out_weight
    }
    
    stmt = insert(Receipt).values(receipt_ins)

    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "receipt add success"}
    except:
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")

        
@dashboard_router.post("/add_component")
async def add(request: Request, #user=Depends(admin_required),
               session: AsyncSession = Depends(get_session)):
    try:
        data = await request.json()
        
        name = data["name"]
        receipt_id = data["receipt_id"]
        weight = data["weight"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")

    component = (await session.execute(select(Component)
               .where(Component.name == name)
               .where(Component.receipt_id == receipt_id)
               .where(Component.status == "active")
    )).first()    
    
    if component != None:
        raise HTTPException(status_code=400, detail="component already exist")
    
    receipt = await session.get(Receipt, receipt_id)
    
    if receipt == None:
        raise HTTPException(status_code=400, detail="receipt not found")
    
    component_ins = {
        "name": name,
        "receipt_id": receipt_id,
        "weight": weight,
        "activation_date": time(),
        "status": "active"
    }
    
    stmt = insert(Component).values(component_ins)

    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "component add success"}
    except:
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")


@dashboard_router.post("/add_param")
async def add(request: Request, #user=Depends(admin_required),
               session: AsyncSession = Depends(get_session)):
    try:
        data = await request.json()
        
        name = data["name"]
        value = data["value"]
        receipt_id = data["receipt_id"]
    except:
        raise HTTPException(status_code=400, detail="incorrect request")
    
    param = (await session.execute(select(Param)
               .where(Param.name == name)
               .where(Param.receipt_id == receipt_id)
               .where(Param.value == value)
               .where(Param.status == "active")
    )).first()    
    
    if param != None:
        raise HTTPException(status_code=400, detail="param already exist")
    
    receipt = await session.get(Receipt, receipt_id)
    
    if receipt == None:
        raise HTTPException(status_code=400, detail="receipt not found")
    
    param_ins = {
        "name": name,
        "receipt_id": receipt_id,
        "value": value,
        "activation_date": time(),
        "status": "active"
    }
    
    stmt = insert(Param).values(param_ins)
    
    try:
        await session.execute(stmt)
        await session.commit()
        return {"detail": "param add success"}
    except:
        await session.rollback()
        raise HTTPException(status_code=500, detail="smth gone wrong")