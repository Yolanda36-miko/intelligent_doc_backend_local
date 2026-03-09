from fastapi import APIRouter,HTTPException
from app.models.schemas import ExtractionResult
from typing import Dict, List

router = APIRouter()

# 模拟缓存（生产环境替换为Redis/数据库）
task_result_cache: Dict[str, dict] = {}

@router.get("/result/{task_id}", response_model=ExtractionResult)
async def get_result(task_id: str):
    #检查任务是否存在
    if task_id not in task_result_cache:
        raise HTTPException(status_code=404, detail=f"任务ID {task_id} 不存在或未完成")
    # TODO: 从数据库或缓存中读取带坐标的结果

    result = task_result_cache[task_id]
    return {
        "task_id": task_id,
        "markdown": result["final_md"],  # 带anchor_id的最终MD
        "chunks": result["trace_map"],  # 溯源坐标信息
        "file_name": result["file_name"],
        "page_count": result["page_count"],
        "block_count": result["block_count"],
        "status": result["status"]
    }
