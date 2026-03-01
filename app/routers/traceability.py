from fastapi import APIRouter
from app.models.schemas import ExtractionResult

router = APIRouter()

@router.get("/result/{task_id}", response_model=ExtractionResult)
async def get_result(task_id: str):
    # TODO: 从数据库或缓存中读取带坐标的结果
    return {"task_id": task_id, "markdown": "测试内容", "chunks": []}