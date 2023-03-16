"""api tests"""
import datetime
import os
import cProfile
from smtplib import SMTPException
from fastapi import HTTPException
import msgspec
import pytest
from shapely import Polygon, from_geojson, difference
from api.routers import zones,users,drones
from api.routers.territories import read_territories,read_territory
from database import drone_events_table, zones_table, drone_updates_table
from database import territories_table
from database.database import create_table
from database.drones_table import CREATE_DRONES_TABLE
from database.incidents import CREATE_INCIDENTS_TABLE
from database.organizations_table import CREATE_ORGANISATIONS_TABLE
from database.territories_table import CREATE_TERRITORY_TABLE, get_orga_area
from database.territory_zones_table import CREATE_TERRITORYZONES_TABLE
from database.users_table import CREATE_USER_TABLE

def improvements():
    """test.
    """
    polygon = territories_table.get_orga_area(1)

    print(datetime.datetime.now())
    drone_updates_table.get_drone_updates(polygon=polygon,
                                              drone_id=1,
                                              get_coords_only=True)
    print(datetime.datetime.now())
    drone_updates_table.get_drone_updates(orga_id=1,
                                              drone_id=1,
                                              get_coords_only=True)
    print(datetime.datetime.now())
    drone_updates_table.get_drone_updates(polygon=polygon,
                                              drone_id=1,
                                              get_coords_only=True)
    print(datetime.datetime.now())
    drone_updates_table.get_drone_updates(orga_id=1,
                                              drone_id=1,
                                              get_coords_only=True)
    print(datetime.datetime.now())
    cProfile.run('improvements()',sort='tottime')

def test_createstatements():
    """function to creates tables"""
    create_table(CREATE_ORGANISATIONS_TABLE)
    create_table(CREATE_USER_TABLE)
    create_table(zones_table.CREATE_ZONE_TABLE)
    create_table(CREATE_DRONES_TABLE)
    create_table(drone_updates_table.CREATE_DRONE_DATA_TABLE)
    create_table(drone_events_table.CREATE_DRONE_EVENT_TABLE)
    create_table(CREATE_TERRITORY_TABLE)
    create_table(CREATE_TERRITORYZONES_TABLE)
    create_table(CREATE_INCIDENTS_TABLE)

@pytest.mark.asyncio
async def test_zones():
    """zone api tests.
    """
    #fetched = zones_table.get_zones()
    user = users.get_user(os.getenv("ADMIN_MAIL"))
    territories = await read_territories(user)
    assert len(territories) <= 2 and len(territories) > 0
    with pytest.raises(HTTPException):
        await read_territory(0,user)
    territory = await read_territory(1,user)
    assert territory.name == 'Landkreis Potsdam-Mittelmark'
    orga_area = get_orga_area(1)
    shapely_one = from_geojson(orga_area)
    shapely_two = from_geojson(msgspec.json.encode(territory.geo_json))

    poly: Polygon = difference(shapely_two, shapely_one)
    assert poly.is_empty


    zones_arr = await zones.get_all_zones(user.organization.id)
    demo_distr = os.getenv("DEMO_DISTRICT")
    demo_distr_two = os.getenv("DEMO_DISTRICT_TWO")
    for fetched in zones_arr:
        assert fetched.district == demo_distr or fetched.district == demo_distr_two, 'Wrong Zone linked.'

    index = len(zones_arr)-1
    zone = await zones.read_zone(zones_arr[index].id,user)
    assert zone == zones_arr[index]
    count = await zones.get_zone_count(user.organization.id)
    assert len(zones_arr) == count

@pytest.mark.asyncio
async def test_drones():
    """drone api tests
    """
    user = users.get_user(os.getenv("ADMIN_MAIL"))
    drone = await drones.read_drone(drone_id=1,current_user=user)
    zone = zones_table.get_zone(drone.zone_id)
    assert [] == await drones.read_drone_events(current_user=user,zone_id=-1)

    try:
        now = datetime.datetime.now()
        zone_events = await drones.read_drone_events(current_user=user,zone_id=zone.id)
        diff = datetime.datetime.now()-now
        print(diff)
    except HTTPException:
        print('No events in zone')
        zone_events = None

    zone_updates = await drones.read_drone_route(current_user=user)
    assert zone_events == zone.events
    assert zone_updates[0].timestamp == zone.last_update
    drone_events_table.insert_demo_events(
                                            zone.lon,
                                            zone.lat,
                                            1,
                                            True
                                            )
    drone_events_table.insert_demo_events(
                                            zone.lon,
                                            zone.lat,
                                            2,
                                            True
                                            )

    polygon = territories_table.get_orga_area(1)
    drone_routes = drone_updates_table.get_drone_updates(polygon=polygon,get_coords_only=True)
    drone_routes_two = drone_updates_table.get_drone_updates(orga_id=1,get_coords_only=True)
    assert drone_routes == drone_routes_two
    assert [] == await drones.read_drone_route(current_user=user,drone_id=-1)
    zone_copunt = await drones.read_drones_count(current_user=user,zone_id=zone.id)
    assert zone_copunt == zone.drone_count
    drone_events_table.insert_demo_events(
                                            8.66697,
                                            49.54887,
                                            1,
                                            True
                                            )
    zone_copunt = await drones.read_drones_count(current_user=user,zone_id=zone.id)
    assert zone_copunt == zone.drone_count-1
    await drones.read_drone_events(current_user=user,drone_id=1)
    await drones.read_drone_events(current_user=user)

    #assert len(d1events) < len(allevents)
    drone_events_table.insert_demo_events(
                                            zone.lon,
                                            zone.lat,
                                            1,
                                            True
                                            )


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

    try:
        await users.register(email=newmail,
                         password='test09Tpw',
                         first_name='testusers',
                         last_name='huhududu',
                         organization=os.getenv("ADMIN_ORGANIZATION"))
    except SMTPException:
        print('Mail not sent')

    except HTTPException:
        print('User already exists')

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
