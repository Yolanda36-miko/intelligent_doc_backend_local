from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import TaskResponse
from app.services import parser_svc,layout_svc
import uuid
import os


router = APIRouter()

@router.post("/ingest", response_model=TaskResponse)
async def ingest_file(file: UploadFile = File(...)):
    """
    接收来自 Dify 或前端的文件上传
    """
    # 1. 验证文件格式 (模块 2 的第一道防线)
    file_ext = os.path.splitext(file.filename)[1].lower()
    if not file.filename.endswith(('.pdf', '.docx', '.xlsx')):
        raise HTTPException(status_code=400, detail="不支持的文件格式")

    # 2. 生成唯一的任务 ID (模块 7 的追踪起点)
    task_id = str(uuid.uuid4())
    # 3. 调用 Service 层保存并预处理文件
    try:
        saved_path = await parser_svc.save_upload_file(file, task_id)
        # TODO: 这里之后会触发 Celery 异步解析任务

        #解析文件生成带占位符的标准MD
        parse_result = parser_svc.parse_document(saved_path)
        if parse_result["status"] == "error":
            raise HTTPException(status_code=500, detail=parse_result["msg"])

        #仅PDF文件执行坐标提取+溯源绑定
        final_md = parse_result["data"]["standard_md"]
        trace_map = []
        page_count = 0
        block_count = 0

        if file_ext == ".pdf":
            #提取PDF坐标
            bbox_list = layout_svc.extract_bbox(saved_path)
            # 绑定溯源信息
            file_name = os.path.basename(saved_path)
            final_md, trace_map = layout_svc.bind_trace_info(final_md, bbox_list, file_name)
            page_count = max([b["page_num"] for b in bbox_list]) if bbox_list else 0
            block_count = len(bbox_list)

    #暂存结果（实际场景存入数据库/缓存，key=task_id） 先简化为内存字典（需替换为Redis/数据库）
        global task_result_cache
        if 'task_result_cache' not in globals():
            task_result_cache = {}

        task_result_cache[task_id] = {
            "file_name": parse_result["data"]["file_name"],
            "parser_engine": parse_result["data"]["parser_engine"],
            "final_md": final_md,
            "trace_map": trace_map,
            "page_count": page_count,
            "block_count": block_count,
            "status": "completed"
        }
        return {
            "task_id": task_id,
            "status": "completed",
            "msg": "文件解析+溯源绑定成功"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
