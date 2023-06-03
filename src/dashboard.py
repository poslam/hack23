from fastapi import APIRouter, Depends
from sqlalchemy import select

from src.auth import login_required
from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product, Receipt


dashboard_router = APIRouter(
    prefix="/dashboard"
)


@dashboard_router.post("/view")
async def view(user=Depends(login_required),
               session: AsyncSession = Depends(get_session)):
    stmt = (select(Product.id.label("product_id"),
                  Product.name.label("product_name"),
                  Receipt.id.label("receipt_id"))
            .join(Receipt, Receipt.product_id == Product.id))
    
    base = (await session.execute(stmt)).all()
    
    if base == []:
        return []
    
    result = []
    
    for receipt in base:
        pass