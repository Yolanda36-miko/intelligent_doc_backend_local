from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- [基础响应] ---
class BaseResponse(BaseModel):
    status: str = Field("success", description="状态: success/error")
    message: Optional[str] = Field(None, description="详细提示")

# --- [模块 2 & 7: 解析与异步性能] ---
class ParsingRequest(BaseModel):
    file_path: str = Field(..., description="宿主机文件的物理绝对路径")
    use_parallel: bool = Field(True, description="模块7: 是否开启切片并行处理")
    parse_mode: str = Field("auto", description="解析模式: fast/ocr/ai")

class TaskResponse(BaseModel):
    task_id: str = Field(..., description="任务唯一标识")
    status: str = Field("processing", description="初始状态")

# --- [模块 4, 6 & 8: 溯源、实体与数字孪生] ---
class BBox(BaseModel):
    rect: List[float] = Field(..., description="[x0, y0, x1, y1] 物理坐标")
    page: int = Field(..., description="所属页码")

class TraceableChunk(BaseModel):
    content: str = Field(..., description="文本片段内容")
    anchor_id: str = Field(..., description="模块4: 全局唯一溯源锚点ID")
    location: BBox
    confidence: float = Field(1.0, description="模块5: AI提取的置信度(0-1)")
    # 模块 6: 实体标签
    entity_type: Optional[str] = Field(None, description="模块6: 实体类型，如‘金额’、‘日期’")

class ExtractionResult(BaseModel):
    task_id: str
    markdown: str = Field(..., description="模块2: 清洗后的全文文本")
    chunks: List[TraceableChunk] = Field(..., description="带溯源信息的语义块列表")

# --- [模块 5: 交互式校验工作台] ---
class CorrectionRequest(BaseModel):
    task_id: str
    anchor_id: str
    new_value: str = Field(..., description="用户手动修正后的数值")
    admin_comment: Optional[str] = Field(None, description="校验备注")

# --- [模块 3 & 8: 智能填表与预览渲染] ---
class FillRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="模块3: 待回填的键值对")
    template_path: str = Field(..., description="目标模板文件路径")
    generate_preview: bool = Field(True, description="模块8: 是否同时生成渲染预览图")

class ExportResponse(BaseResponse):
    download_url: str = Field(..., description="成果文档下载地址")
    preview_url: Optional[str] = Field(None, description="模块8: 坐标高亮后的 PDF 预览流地址")

# --- [模块 9 & 7: 异步监控与运维] ---
class TaskStatus(BaseModel):
    task_id: str
    status: str = Field(..., description="pending/processing/completed/failed")
    progress: int = Field(0, description="0-100 的整数进度")
    current_msg: str = Field(..., description="模块7: 当前步骤实时描述")

class SystemMetrics(BaseModel):
    latency_ms: float = Field(..., description="平均处理时延")
    memory_usage: float = Field(..., description="16GB 内存当前占用率 (%)")
    active_workers: int = Field(..., description="模块7: 当前活跃的并行进程数")