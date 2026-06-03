from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.activity import Activity
from app.models.user import User

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("")
async def list_activity(limit: int = 50, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = select(Activity).where(Activity.user_id == current_user.id).order_by(Activity.created_at.desc()).limit(limit)
    r = await db.execute(q)
    rows = r.scalars().all()
    return [
        {
            "id": a.id,
            "action": a.action,
            "subject_type": a.subject_type,
            "subject_id": a.subject_id,
            "details": a.details,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in rows
    ]
