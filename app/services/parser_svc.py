import os
import shutil
from fastapi import UploadFile

# 确保上传目录存在
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(file: UploadFile, task_id: str) -> str:
    """
    将上传的文件持久化到磁盘，为后续 MinerU 解析做准备
    """
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{task_id}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, file_name)
    
    # 使用 shutil 块拷贝，保护 16GB 内存不被大文件撑爆
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return dest_path