from fastapi import APIRouter, UploadFile, Depends, HTTPException, status, Request
import uuid
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies.auth import get_current_user
from app.database import get_db
from app.services import storage_service
from app.models.file import File
from app.models.user import User

router = APIRouter(tags=["Files"], prefix="/api/files")


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # basic size check
    contents = await file.read()
    if len(contents) > request.app.extra.get("settings").MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    key = f"{current_user.id}/{str(uuid.uuid4())}_{file.filename}"
    # upload to S3 (async wrapper)
    await storage_service.upload_bytes(key, contents, file.content_type)
    # create DB record
    f = File(owner_id=current_user.id, filename=file.filename, content_type=file.content_type, size=len(contents), s3_key=key)
    db.add(f)
    await db.flush()
    return {"id": f.id, "filename": f.filename, "size": f.size, "url": storage_service.build_s3_url(key)}


@router.get("")
async def list_files(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = select(File).where(File.owner_id == current_user.id, File.is_deleted == False)
    r = await db.execute(q)
    items = r.scalars().all()
    result = []
    for it in items:
        result.append({
            "id": it.id,
            "filename": it.filename,
            "size": it.size,
            "content_type": it.content_type,
            "url": storage_service.build_s3_url(it.s3_key),
            "created_at": it.created_at.isoformat() if it.created_at else None,
        })
    return result
