from fastapi import APIRouter
from app.models.schemas import TaskResponse, ParsingRequest

router = APIRouter()

@router.post("/ingest", response_model=TaskResponse)
async def ingest_file(request: ParsingRequest):
    # TODO: 调用 services/parser_svc.py 进行异步解析
    return {"task_id": "mock_id_123", "status": "processing"}