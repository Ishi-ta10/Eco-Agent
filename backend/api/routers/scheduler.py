"""
Scheduler endpoints router
"""
from fastapi import APIRouter, UploadFile, File, Query, Body
from typing import Optional
from ..services import scheduler_service
from ..schemas.scheduler import SchedulerConfig, SchedulerStatus, SendNowRequest
from ..schemas.common import SuccessResponse

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


@router.get("/config")
async def get_scheduler_config():
    """Get current scheduler configuration"""
    return scheduler_service.load_scheduler_config()


@router.put("/config")
async def update_scheduler_config(config: SchedulerConfig):
    """Update scheduler configuration"""
    return scheduler_service.save_scheduler_config(config.dict())


@router.get("/status")
async def get_scheduler_status():
    """Get scheduler status"""
    return scheduler_service.get_scheduler_status()


@router.post("/start")
async def start_scheduler(
    payload: Optional[dict] = Body(default=None),
    send_time: Optional[str] = Query(default=None, description="Send time in HH:MM format"),
):
    """Start background scheduler"""
    selected_time = send_time
    if payload and isinstance(payload, dict):
        selected_time = payload.get("send_time", selected_time)
    if not selected_time:
        selected_time = "10:00"

    return scheduler_service.start_scheduler(selected_time)


@router.post("/stop")
async def stop_scheduler():
    """Stop background scheduler"""
    return scheduler_service.stop_scheduler()


@router.post("/send-now")
async def send_email_now():
    """Send test email immediately"""
    return scheduler_service.send_email_now()


@router.get("/debug/test-email")
async def test_email_generation():
    """Debug endpoint to test email generation"""
    result = scheduler_service.send_email_now()
    return result


@router.get("/history")
async def get_scheduler_history(limit: int = Query(10, description="Number of entries to return")):
    """Get scheduler run history"""
    return scheduler_service.load_scheduler_history(limit)


@router.post("/upload-template")
async def upload_template(file: UploadFile = File(...)):
    """Upload custom Excel template"""
    # Save file to uploads directory
    from pathlib import Path
    import shutil

    upload_dir = Path(__file__).parent.parent.parent / "energy-dashboard" / "uploaded_templates"
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return scheduler_service.upload_template(str(file_path))
