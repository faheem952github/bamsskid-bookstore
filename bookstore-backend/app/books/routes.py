from fastapi import APIRouter

books_router = APIRouter(prefix="/books", tags=["Books"])


@books_router.get("/")
async def get_books_info():
    return {"message": "Hello from Books"}
