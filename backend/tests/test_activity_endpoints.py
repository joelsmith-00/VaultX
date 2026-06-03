import uuid
import pytest

from app.models.user import User
from app.services.activity_service import log_activity
from app.utils.security import hash_password, create_access_token


@pytest.mark.asyncio
async def test_activity_listing_and_pagination(db_session, client):
    # create test user
    user = User(id=str(uuid.uuid4()), email='tester@example.com', username='tester', password_hash=hash_password('pass'))
    db_session.add(user)
    await db_session.flush()

    # insert 25 activity rows
    for i in range(25):
        await log_activity(db_session, user.id, 'test_action', 'subject', f'subj_{i}', {'idx': i})

    # create access token
    token = create_access_token({'sub': user.id})

    # request first page (default limit 50 but we'll use limit=10)
    headers = {'Authorization': f'Bearer {token}'}
    resp = await client.get('/api/activity?limit=10&offset=0', headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert 'items' in data and 'next_offset' in data
    assert len(data['items']) == 10
    assert data['next_offset'] == 10

    # request second page
    resp2 = await client.get(f"/api/activity?limit=10&offset={data['next_offset']}", headers=headers)
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert len(d2['items']) == 10
    assert d2['next_offset'] == 20

    # request last page
    resp3 = await client.get(f"/api/activity?limit=10&offset={d2['next_offset']}", headers=headers)
    assert resp3.status_code == 200
    d3 = resp3.json()
    assert len(d3['items']) == 5
    assert d3['next_offset'] is None
