from bson import ObjectId

from source.app.users.schemas import User, UserCreate, UserUpdate, UserUpdateBase
from source.app.users.utils import check_username
from source.core.database import db


async def check_username_user(username: str) -> dict:
    available = await check_username(username=username)
    return {"username": username, "available": available}


async def create_user(user: User) -> dict:
    if await check_username(username=user.username):
        user = UserCreate(**user.dict())
        new_user = await db["user"].insert_one(user.dict())
        created_user = await db["user"].find_one({"_id": new_user.inserted_id})
        return created_user


async def update_user(user_id: ObjectId, user: UserUpdate) -> dict:
    if not user.username or await check_username(
        username=user.username, user_id=user_id
    ):
        user = UserUpdateBase(**user.dict())
        fields_to_update = {k: v for k, v in user.dict().items() if v is not None}
        await db["user"].update_one({"_id": user_id}, {"$set": fields_to_update})
        updated_user = await db["user"].find_one({"_id": user_id})
        return updated_user


async def get_user(username: str) -> dict:
    if user := await db["user"].find_one({"username": username}):
        return user
