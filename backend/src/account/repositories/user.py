from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.account.schemas import CreateUserSchema, UpdateUserSchema
from src.account.models import User
from sqlalchemy import Select, Update, Delete


class UserRepository():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_schema: CreateUserSchema):
        user = User(
            first_name = user_schema.first_name,
            last_name = user_schema.last_name,
            company = user_schema.company,
            email = user_schema.email,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_from_dict(self, user_data: dict):
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: int, user_schema: UpdateUserSchema):
        user_dict = user_schema.dict(exclude_unset=True)
        query = Update(User).where(User.id == user_id).values(**user_dict)
        await self.session.execute(query)
        await self.session.commit()
        updated_user = await self.session.get(User, user_id)
        return updated_user

    async def update_password(self, user_id: int, hashed_password: str):
        query = Update(User).where(User.id == user_id).values(password=hashed_password)
        await self.session.execute(query)
        await self.session.commit()

    async def delete(self, user_id: int):
        query = Delete(User).where(User.id == user_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NoResultFound(f"User with id {user_id} not found")
        await self.session.commit()
        return {"detail": "success"}

    async def get_by_id(self, user_id: int):
        user = await self.session.get(User, user_id)
        return user

    async def get_by_email(self, email: str):
        query = Select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self):
        query = Select(User)
        result = await self.session.execute(query)
        users = result.scalars().all()
        return users
