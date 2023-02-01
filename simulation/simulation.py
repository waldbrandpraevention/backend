import requests

URL = "kiwa.tech/api/"
NUM_DRONES = 3

drones = [
    {
        name: str = "bob",
        type: str = "type a"
        flight_range: float = 1000000
        cc_range: float  = 100000
        flight_time: float = 100000
        last_update: datetime | None = None
        zone: str = "insert zone"
        droneowner_id: int | None = None  
    },
]


#login
for i in range(NUM_DRONES):
    requests.post(URL + "drones/login/", data=drones[i]) 