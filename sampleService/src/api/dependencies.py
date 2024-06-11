from collections.abc import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from db.session import SessionLocal

# async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
#     async with SessionLocal() as session:
#         yield session
        
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()