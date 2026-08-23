from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate

router = APIRouter(tags=["customers"])


@router.post("/customers")
async def create_customer(
    payload: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Check if customer already exists
    result = await db.execute(
        select(Customer).where(Customer.email == payload.email)
    )
    existing_customer = result.scalar_one_or_none()

    if existing_customer:
        raise HTTPException(
            status_code=409,
            detail="Customer with this email already exists"
        )

    # 2. Create new customer
    customer = Customer(
        email=payload.email,
        preferred_language=payload.preferred_language
    )

    db.add(customer)

    try:
        await db.commit()
        await db.refresh(customer)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Failed to create customer"
        )

    return {
        "id": customer.id,
        "email": customer.email,
        "preferred_language": customer.preferred_language
    }

