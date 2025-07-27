from fastapi import APIRouter


router = APIRouter(
    prefix="/test",
    tags=["Test"]
)

@router.get("/health")
def health_handler():
    return {"work": "success"}