from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import TaskResponse
from app.services import parser_svc
import uuid

router = APIRouter()

@router.post("/ingest", response_model=TaskResponse)
async def ingest_file(file: UploadFile = File(...)):
    """
    接收来自 Dify 或前端的文件上传
    """
    # 1. 验证文件格式 (模块 2 的第一道防线)
    if not file.filename.endswith(('.pdf', '.docx', '.xlsx')):
        raise HTTPException(status_code=400, detail="不支持的文件格式")

    # 2. 生成唯一的任务 ID (模块 7 的追踪起点)
    task_id = str(uuid.uuid4())
    
    # 3. 调用 Service 层保存并预处理文件
    try:
        saved_path = await parser_svc.save_upload_file(file, task_id)
        # TODO: 这里之后会触发 Celery 异步解析任务
        return {"task_id": task_id, "status": "file_received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")