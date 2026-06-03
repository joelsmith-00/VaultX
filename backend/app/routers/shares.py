from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.share import Share
from app.models.file import File
from app.models.folder import Folder
from app.utils import generate_verification_token, hash_password
from app.config import settings
from app.utils import verify_password
from app.services import generate_presigned_url
from datetime import timezone
from app.services.activity_service import log_activity

router = APIRouter(tags=["Shares"], prefix="/api/shares")


@router.post("/create")
async def create_share(item_type: str, item_id: str, password: str | None = None, expires_minutes: int | None = None, max_uses: int | None = None, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    # validate ownership
    if item_type == "file":
        q = select(File).where(File.id == item_id, File.owner_id == current_user.id)
        r = await db.execute(q)
        obj = r.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    elif item_type == "folder":
        q = select(Folder).where(Folder.id == item_id, Folder.owner_id == current_user.id)
        r = await db.execute(q)
        obj = r.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item_type")

    token = generate_verification_token()
    phash = hash_password(password) if password else None
    expires_at = (datetime.utcnow() + timedelta(minutes=expires_minutes)) if expires_minutes else None
    share = Share(owner_id=current_user.id, file_id=item_id if item_type == "file" else None, folder_id=item_id if item_type == "folder" else None, token=token, password_hash=phash, expires_at=expires_at, max_uses=max_uses)
    db.add(share)
    await db.flush()
    url = f"{settings.FRONTEND_URL.rstrip('/')}" + f"/share/{token}"
    # log creation
    await log_activity(db, current_user.id, "share_create", "share", share.id, {"token": token, "url": url})
    return {"id": share.id, "token": token, "url": url}


@router.get("/info/{token}")
async def get_share_info(token: str, db: AsyncSession = Depends(get_db)):
    q = select(Share).where(Share.token == token, Share.is_active == True)
    r = await db.execute(q)
    share = r.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    return {"id": share.id, "file_id": share.file_id, "folder_id": share.folder_id, "expires_at": share.expires_at, "max_uses": share.max_uses, "uses": share.uses}



@router.get("/me")
async def list_my_shares(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    q = select(Share).where(Share.owner_id == current_user.id)
    r = await db.execute(q)
    rows = r.scalars().all()
    return [{"id": s.id, "token": s.token, "file_id": s.file_id, "folder_id": s.folder_id, "uses": s.uses, "max_uses": s.max_uses, "is_active": s.is_active, "created_at": s.created_at} for s in rows]


@router.post("/access")
async def access_share(token: str, password: str | None = None, db: AsyncSession = Depends(get_db)):
    q = select(Share).where(Share.token == token, Share.is_active == True)
    r = await db.execute(q)
    share = r.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    # check expiry
    if share.expires_at:
        now = datetime.now(timezone.utc)
        if share.expires_at < now:
            share.is_active = False
            await db.flush()
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share expired")
    # check password
    if share.password_hash:
        if not password or not verify_password(password, share.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # check uses
    if share.max_uses is not None and share.uses >= (share.max_uses or 0):
        share.is_active = False
        await db.flush()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share max uses exceeded")

    # increment uses
    share.uses = (share.uses or 0) + 1
    if share.max_uses is not None and share.uses >= share.max_uses:
        share.is_active = False
    await db.flush()
    # log access (anonymous user) - use owner id as subject if available
    await log_activity(db, share.owner_id, "share_access", "share", share.id, {"token": share.token, "uses": share.uses})

    # If file share, return presigned URL
    if share.file_id:
        fq = select(File).where(File.id == share.file_id)
        fr = await db.execute(fq)
        file = fr.scalar_one_or_none()
        if not file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        url = generate_presigned_url(file.s3_key, expires_in=3600)
        return {"type": "file", "file": {"id": file.id, "filename": file.filename, "content_type": file.content_type, "size": file.size}, "url": url}

    # Folder share - return metadata (file listing not yet implemented)
    if share.folder_id:
        return {"type": "folder", "folder_id": share.folder_id, "message": "Folder share access - listing not implemented"}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid share")



@router.post("/{share_id}/revoke")
async def revoke_share(share_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    q = select(Share).where(Share.id == share_id, Share.owner_id == current_user.id)
    r = await db.execute(q)
    share = r.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    share.is_active = False
    await db.flush()
    await log_activity(db, current_user.id, "share_revoke", "share", share.id, {"token": share.token})
    return {"status": "ok"}
