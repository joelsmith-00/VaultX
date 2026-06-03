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
    return {"id": share.id, "token": token, "url": url}


@router.get("/info/{token}")
async def get_share_info(token: str, db: AsyncSession = Depends(get_db)):
    q = select(Share).where(Share.token == token, Share.is_active == True)
    r = await db.execute(q)
    share = r.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    return {"id": share.id, "file_id": share.file_id, "folder_id": share.folder_id, "expires_at": share.expires_at, "max_uses": share.max_uses, "uses": share.uses}
