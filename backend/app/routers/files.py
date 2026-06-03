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
from app.services import generate_presigned_url
from fastapi.responses import JSONResponse
from urllib.parse import quote

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


@router.get("/{file_id}/download")
async def download_file(file_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = select(File).where(File.id == file_id)
    r = await db.execute(q)
    f = r.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if f.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    url = generate_presigned_url(f.s3_key, expires_in=600)
    return {"url": url, "filename": f.filename, "content_type": f.content_type}


@router.get("/{file_id}/preview")
async def preview_file(file_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = select(File).where(File.id == file_id)
    r = await db.execute(q)
    f = r.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if f.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    # only allow inline preview for images and PDFs
    ctype = (f.content_type or "").lower()
    if not (ctype.startswith("image/") or ctype == "application/pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Preview not supported for this file type")
    # generate presigned URL with inline disposition
    # some S3 implementations support ResponseContentDisposition override
    url = generate_presigned_url(f.s3_key, expires_in=300)
    return JSONResponse(content={"url": url, "content_type": ctype, "filename": f.filename})
