from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import parsing, traceability, async_ops, actions

# 1. 初始化 FastAPI
app = FastAPI(
    title="智能文档交互系统-本地后端引擎",
    description="支持 9 大核心模块的竞赛级 AI 后端服务",
    version="1.0.0"
)

# 2. 配置跨域，确保 Dify 容器和前端能访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 开发阶段允许所有来源
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 核心：将 4 个工程模块挂载到主服务
app.include_router(parsing.router, prefix="/v1/parsing", tags=["解析网关"])
app.include_router(traceability.router, prefix="/v1/trace", tags=["溯源引擎"])
app.include_router(async_ops.router, prefix="/v1/async", tags=["异步监控"])
app.include_router(actions.router, prefix="/v1/actions", tags=["回填渲染"])

@app.get("/")
async def health_check():
    return {"status": "success", "info": "后端骨架已全线连通，16GB 内存防御系统运行中"}