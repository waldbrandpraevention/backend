"""api tests"""
import os
import sys
import pytest
sys.path.append('../backend')
from api.routers import zones,users

@pytest.mark.asyncio
async def test_zones():
    user = users.get_user(os.getenv("ADMIN_MAIL"))
    zones_arr = await zones.get_all_zones(user.organization.id)
    demo_distr = os.getenv("DEMO_DISTRICT")
    for fetched in zones_arr:
        assert fetched.district == demo_distr, 'Wrong Zone linked.'
    index = len(zones_arr)-1
    zone = await zones.read_zone(zones_arr[index].id,user)
    assert zone == zones_arr[index]
    count = await zones.get_zone_count(user.organization.id)
    assert len(zones_arr) == count
