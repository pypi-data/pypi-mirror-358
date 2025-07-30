from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from .models import User
from db2_hj3415.common.db_ops import get_collection
from db2_hj3415.stockwise import DB_NAME
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "user"  # 또는 "users"

async def save(user_data: User, client: AsyncIOMotorClient) -> dict:
    if not user_data:
        mylogger.warning("User 데이터 없음 - 저장 생략")
        return {"status": "unchanged"}

    collection = get_collection(client, DB_NAME, COL_NAME)

    # 인덱스는 앱 초기화 시점에 1회만 생성
    # 이메일 유니크 인덱스
    await collection.create_index("email", unique=True)

    data = user_data.model_dump(by_alias=True, exclude_unset=True)

    # 가입일 기본값 보정
    if "created_at" not in data:
        data["created_at"] = datetime.utcnow()

    filter_ = {"email": user_data.email}

    result = await collection.update_one(
        filter_,
        {"$set": data},
        upsert=True
    )

    if result.upserted_id:
        return {"status": "inserted", "id": str(result.upserted_id)}
    elif result.modified_count:
        return {"status": "updated"}
    else:
        return {"status": "unchanged"}


async def get_user_by_email(email: str, client: AsyncIOMotorClient) -> User | None:
    collection = get_collection(client, DB_NAME, COL_NAME)

    doc = await collection.find_one({"email": email})
    if doc:
        return User(**doc)  # Pydantic 모델로 역직렬화
    return None