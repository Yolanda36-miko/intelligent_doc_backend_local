from fastapi import APIRouter
from app.models.schemas import TaskStatus, SystemMetrics

router = APIRouter()

@router.get("/status/{task_id}", response_model=TaskStatus)
async def check_status(task_id: str):
    return {"task_id": task_id, "status": "completed", "progress": 100, "current_msg": "已完成"}

@router.get("/metrics", response_model=SystemMetrics)
async def get_metrics():
    return {"latency_ms": 120.5, "memory_mb": 450.0, "token_cost": 0.05}