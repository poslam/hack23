from fastapi import APIRouter, Depends
from sqlalchemy import select

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
        