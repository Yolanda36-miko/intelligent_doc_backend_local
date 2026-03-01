from fastapi import APIRouter
from app.models.schemas import FillRequest, ExportResponse

router = APIRouter()

@router.post("/fill-template", response_model=ExportResponse)
async def fill_template(request: FillRequest):
    return {"status": "success", "download_url": "http://example.com/file.xlsx"}