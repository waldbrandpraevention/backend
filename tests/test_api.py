"""api tests"""
import os
import sys
import pytest
sys.path.append('../backend')
from api.routers import zones,drones,users

@pytest.mark.asyncio
async def test_zones():
    user = users.get_user(os.getenv("ADMIN_MAIL"))
    zones_arr = await zones.get_all_zones(user.organization.id)
    index = len(zones_arr)-1
    zone = await zones.get_zone(zones_arr[index].name,user.organization.id)
    assert zone == zones_arr[index]
    count = await zones.get_zone_count(user.organization.id)
    assert len(zones_arr) == count
