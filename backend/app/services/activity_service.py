from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity import Activity


async def log_activity(db: AsyncSession, user_id: str, action: str, subject_type: str | None = None, subject_id: str | None = None, details: dict | None = None):
    act = Activity(user_id=user_id, action=action, subject_type=subject_type, subject_id=subject_id, details=details)
    db.add(act)
    await db.flush()
    return act
