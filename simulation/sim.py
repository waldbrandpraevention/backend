import requests

URL = "kiwa.tech/api/"
NUM_DRONES = 3

class drone:
    speed: float,
    lat: float,
    long: float,
    id: int,
    name: str,
    type: str,
    flight_range: float,
    cc_range: float,
    flight_time: float,
    last_update: datetime,
    zone: str,
    droneowner_id:,  
    


drones = [
    {
        "name": "bob",
        "type": "type a",
        "flight_range": 1000000,
        "cc_range": 100000,
        "flight_time": 100000,
        "last_update": None,
        "zone": "insert zone",
        "droneowner_id": None  
    },
]

token_list = []
zones_list = []


#login
for i in range(NUM_DRONES):
    token = requests.post(URL + "drones/login/", data=drones[i]) 
    token_list.append(token)
    zone = requests.get(URL + "zones/"drones[i][zone])



#simulate
for i in range(NUM_DRONES):
    token = requests.post(URL + "drones/login/", data=drones[i]) 
    token_list.append(token)

#simulate
for i in range(NUM_DRONES):
    token = requests.post(URL + "drones/login/", data=drones[i]) 
    token_list.append(token)
