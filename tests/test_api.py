"""api tests"""
import datetime
import os
import cProfile
import random
from smtplib import SMTPException
import pytz
from fastapi import HTTPException
import msgspec
import pytest
from shapely import Polygon, from_geojson, difference
from api.routers import zones,users,drones
from api.routers.incidents import alarm_team, all_incidents
from api.routers.territories import read_territories,read_territory
from database import drone_events_table, zones_table, drone_updates_table
from database import territories_table
from database import drones_table
from database.database import TIMEZONE, create_table
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
async def test_incidents():
    """incident api tests.
    """
    user = users.get_user(os.getenv("ADMIN_MAIL"))
    await alarm_team('test_name',
               'test_loc',
               'test_type',
                'test_notes',
                user)

    alarms = await all_incidents(user)
    assert alarms[len(alarms)-1].notes == 'test_notes'
    assert alarms[len(alarms)-1].location == 'test_loc'

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
        assert fetched.district in (demo_distr, demo_distr_two), 'Wrong Zone linked.'

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
    name = f'trinity{random.randint(0, 1000)}'
    drone = drones_table.create_drone(
                name=name,
                drone_type="Unmanned Aerial Vehicle",
                cc_range=7.5,
                flight_range=100.0,
                flight_time=90.0
            )
    lat = float(os.getenv("DEMO_LAT"))
    lon = float(os.getenv("DEMO_LONG"))
    timestamp = datetime.datetime.utcnow()
    drone_updates_table.create_drone_update(
            drone_id=drone.id,
            timestamp=timestamp,
            longitude=lon,
            latitude=lat,
            flight_range=50,
            flight_time=50
        )
    zones_table.set_update_for_coordinate(lon, lat, timestamp)
    read_drone = await drones.read_drone(drone_id=drone.id,current_user=user)
    assert drone.name == read_drone.name and drone.flight_range == read_drone.flight_range

    zone = zones_table.get_zone(read_drone.zone_id)
    zone_copunt = await drones.read_drones_count(current_user=user,zone_id=zone.id)
    assert [] == await drones.read_drone_events(current_user=user,zone_id=-1)

    try:
        zone_events = await drones.read_drone_events(current_user=user,zone_id=zone.id)
    except HTTPException:
        print('No events in zone')
        zone_events = None

    zone_updates = await drones.read_drone_route(current_user=user,drone_id=drone.id)
    assert zone_events == zone.events
    assert zone_updates[0].timestamp == zone.last_update

    polygon = territories_table.get_orga_area(1)
    drone_routes = drone_updates_table.get_drone_updates(polygon=polygon,get_coords_only=True)
    drone_routes_two = drone_updates_table.get_drone_updates(orga_id=1,get_coords_only=True)
    assert drone_routes == drone_routes_two
    assert [] == await drones.read_drone_route(current_user=user,drone_id=-1)

    assert zone_copunt == zone.drone_count
    newtimestamp = timestamp + datetime.timedelta(seconds=5)
    drone_updates_table.create_drone_update(
            drone_id=drone.id,
            timestamp=newtimestamp,
            longitude=8.66697,
            latitude=49.54887,
            flight_range=50,
            flight_time=50
        )

    zones_table.set_update_for_coordinate(8.66697, 49.54887, newtimestamp)

    zone_copunt = await drones.read_drones_count(current_user=user,zone_id=zone.id)
    assert zone_copunt == zone.drone_count-1 or zone.drone_count == 1
    await drones.read_drone_events(current_user=user,drone_id=1)
    await drones.read_drone_events(current_user=user)

    drone_dict = await drones.drone_signup(
        'name',
        'type',
        100,
        100,
        100,
        user
    )
    drone = drone_dict['drone']
    await drones.drone_update(
            drone_id=2,
            timestamp=newtimestamp,
            lon=8.66697,
            lat=48.54887,
            flight_range=50,
            flight_time=50,
            current_drone_token=drone_dict['token']
            )
    second_zone = zones_table.get_zone_of_coordinate(8.66697,48.54887)
    tz_timestamp = newtimestamp.astimezone(pytz.timezone(TIMEZONE))
    assert second_zone.last_update == tz_timestamp

    newtimestamp = newtimestamp + datetime.timedelta(seconds=5)
    drone_updates_table.create_drone_update(
            drone_id=2,
            timestamp=timestamp,
            longitude=zone.lon,
            latitude=zone.lat,
            flight_range=50,
            flight_time=50
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
