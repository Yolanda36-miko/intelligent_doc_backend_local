# 智能文档交互系统 - 后端引擎 (Local Version)

🚀 **架构**：FastAPI + Celery + Redis

## 📂 目录指引
- `app/routers/`: 接口层 (定义 9 大模块的 API 路径)
- `app/services/`: 逻辑层 (队员编写 MinerU、PyMuPDF、Pandas 逻辑的地方)
- `app/models/`: 数据契约 (统一 9 模块的输入输出标准)
- `celery_worker/`: 异步中心 (处理耗时解析，保护 16GB 内存)

## 实例结构，仅供参考
- intelligent_doc_backend\app\services\parser_svc.py
- intelligent_doc_backend\app\routers\parsing.py

## 🛠️ 快速启动
1. **创建环境**: `python -m venv light.venv`
2. **激活环境**: `.\light.venv\Scripts\activate`
3. **安装依赖**: `pip install -r requirements.txt`
4. **启动服务**: `uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload`
5. **接口文档**: 访问 `http://localhost:8001/docs`

⚠️ **开发红线**: 严禁修改 `app/models/schemas.py`；处理大文件后必须显式释放内存。