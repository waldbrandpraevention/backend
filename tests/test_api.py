"""api tests"""
import os
import sys
import pytest
sys.path.append('../backend')
from api.routers import zones,users,drones
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_zones():
    """zone api tests.
    """
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

@pytest.mark.asyncio
async def test_drones():
    """zone api tests.
    """
    user = users.get_user(os.getenv("ADMIN_MAIL"))
    drone = await drones.read_drone(drone_id=1,current_user=user)
    with pytest.raises(HTTPException):
        await drones.read_drone_events(current_user=user,zone_id=-1)
    zone_events = await drones.read_drone_events(current_user=user,zone_id=drone.zone_id)
    d1events = await drones.read_drone_events(current_user=user,drone_id=1)
    allevents = await drones.read_drone_events(current_user=user)

    assert len(d1events) < len(allevents)
    


@pytest.mark.asyncio
async def test_users():
    """user api tests
    """
    adminmail = os.getenv("ADMIN_MAIL")
    user = users.get_user(adminmail)
    first_name = f'{user.first_name}s'
    last_name = f'{user.last_name}s'
    email = 'Hans@admin.org'

    newmail = 'mailtest66@mail.de'

    await users.register(email=newmail,
                         password='test09Tpw',
                         first_name='testusers',
                         last_name='huhududu',
                         organization=os.getenv("ADMIN_ORGANIZATION"))
    newuser = users.get_user(newmail)
    await users.delete_users(newuser.id,user)

    await users.update_user_info(current_user=user,first_name=first_name,last_name=last_name)
    updated = users.get_user(adminmail)
    assert updated.first_name == first_name
    assert updated.last_name == last_name

    verified = not updated.email_verified
    await users.admin_update_user_info(
        update_user_id=user.id,
        current_user=updated,
        email_verified=verified,#
        email=email
    )
    updated = users.get_user(email)
    assert updated.first_name == first_name
    assert updated.last_name == last_name
    assert updated.email == email
    assert updated.email_verified == verified

    await users.update_user_info(current_user=updated,
                                 email=adminmail,
                                 first_name='Admin',
                                 last_name='Admin')
