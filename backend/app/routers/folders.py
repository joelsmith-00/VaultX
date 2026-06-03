from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.folder import Folder
from app.models.user import User

router = APIRouter(tags=["Folders"], prefix="/api/folders")


@router.post("/")
async def create_folder(name: str, parent_id: str | None = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    f = Folder(owner_id=current_user.id, name=name, parent_id=parent_id)
    db.add(f)
    await db.flush()
    return {"id": f.id, "name": f.name, "parent_id": f.parent_id}


@router.get("/")
async def list_folders(parent_id: str | None = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = select(Folder).where(Folder.owner_id == current_user.id)
    if parent_id is None:
        q = q.where(Folder.parent_id == None)
    else:
        q = q.where(Folder.parent_id == parent_id)
    r = await db.execute(q)
    items = r.scalars().all()
    return [{"id": it.id, "name": it.name, "parent_id": it.parent_id} for it in items]
