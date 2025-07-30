from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import InsertOne, DESCENDING
from db2_hj3415.nfs import Dart, DB_NAME, get_collection
from datetime import datetime, timezone, timedelta

COL_NAME = "dart"

async def save_many(many_data: list[Dart], client: AsyncIOMotorClient) -> dict:
    if not many_data:
        return {"inserted_count": 0, "skipped": 0}

    collection = get_collection(client, DB_NAME, COL_NAME)

    # unique index 보장용 (이미 설정되었는지 확인)
    await collection.create_index("rcept_no", unique=True)

    ops = []
    skipped = 0

    for item in many_data:
        doc = item.model_dump(mode="json", exclude={"id"})  # _id는 제외
        ops.append(InsertOne(doc))

    try:
        result = await collection.bulk_write(ops, ordered=False)
        return {"inserted_count": result.inserted_count, "skipped": skipped}
    except Exception as e:
        return {"error": str(e)}


async def get_data_last_n_days(code: str, client: AsyncIOMotorClient, days:int = 30) -> list[Dart]:
    """
    지정한 종목 코드(code)에 대해 최근 N일(days) 동안의 DART 데이터를 비동기로 조회합니다.

    MongoDB 컬렉션에서 날짜 기준으로 N일 이전(cutoff) 이후의 문서들을 조회하며,
    결과는 최신 날짜순(DESCENDING)으로 정렬됩니다.

    Parameters:
        code (str): 조회할 종목 코드 (예: '005930').
        client (AsyncIOMotorClient): 비동기 MongoDB 클라이언트.
        days (int, optional): 며칠 전까지의 데이터를 가져올지 설정 (기본값: 30일).

    Returns:
        list[Dart]: Dart Pydantic 모델의 리스트. 데이터가 없으면 빈 리스트 반환.
    """
    collection = get_collection(client, DB_NAME, COL_NAME)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    cursor = collection.find(
        {
            "코드": code,
            "날짜": {"$gte": cutoff}
        }
    ).sort("날짜", DESCENDING)

    docs = await cursor.to_list(length=None)
    if not docs:
        return []
    else:
        darts = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            darts.append(Dart(**doc))
        return darts


async def get_data_today(client: AsyncIOMotorClient) -> list[Dart]:
    """
    오늘 날짜의 DART 데이터를 비동기로 조회합니다.

    MongoDB 컬렉션에서 오늘 날짜에 해당하는 모든 종목의 문서를 조회하며,
    결과는 '날짜' 필드를 기준으로 내림차순 정렬됩니다.

    Parameters:
        client (AsyncIOMotorClient): 비동기 MongoDB 클라이언트.

    Returns:
        List[Dart]: Dart Pydantic 모델의 리스트. 없으면 빈 리스트.
    """
    collection = get_collection(client, DB_NAME, COL_NAME)

    # 오늘 00:00 ~ 내일 00:00 사이의 UTC 기준
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    start_of_next_day = start_of_day + timedelta(days=1)

    cursor = collection.find(
        {
            "날짜": {
                "$gte": start_of_day,
                "$lt": start_of_next_day
            }
        }
    ).sort("날짜", DESCENDING)

    docs = await cursor.to_list(length=None)
    if not docs:
        return []

    return [Dart(**{**doc, "_id": str(doc["_id"])}) for doc in docs]
