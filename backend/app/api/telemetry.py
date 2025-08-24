from fastapi import APIRouter

router = APIRouter()

@router.get("/workers")
def workers():
    return {"workers": []}
