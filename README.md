<h1 align="center">Waldbrandprävention Backend</h1>
<p align="center">   
    <img width="320" height="160" src="img/logo-v1.svg">
</p>

<div align="center">

[![pylint](https://img.shields.io/github/actions/workflow/status/waldbrandpraevention/backend/pylint.yml?branch=main&style=for-the-badge&label=ci)](https://github.com/waldbrandpraevention/backend/actions/workflows/Pylint.yml)
![](https://img.shields.io/github/actions/workflow/status/waldbrandpraevention/backend/docker-image.yml?branch=main&style=for-the-badge&label=docker)
![](https://img.shields.io/github/commit-activity/m/waldbrandpraevention/backend?style=for-the-badge&label=commits)
![](https://img.shields.io/docker/image-size/waldbrand/backend?style=for-the-badge&label=image&color=orange)
[![](https://img.shields.io/codefactor/grade/github/waldbrandpraevention/backend?style=for-the-badge)](https://www.codefactor.io/repository/github/waldbrandpraevention/backend/issues/main)


![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

<p align="center">
  <img src="img/db.png" width="1200" title="hover text">
</p>

</div>

## Einleitung
Im Backend können Drohnen über eingerichtete [API Endpunkte](#api-docs) ihre Updates (Standort und Timestamp) und Events (Detektion von Feuer und/oder Rauch) schicken. Diese Daten werden anschließend in der Datenbank gespeichert. Beim Anfragen der Daten wird jederzeit sichergestellt, dass Nutzer\*innen nur auf Daten innerhalb des Territoriums ihrer Organisation zugreifen können.

## Datenbank
Die Datenbank lässt sich in zwei Bereiche teilen:

### Nutzer und Orgadaten
In der Tabelle 'users' werden Nutzer\*innen angelegt. Hierbei muss die id einer Organisation angegeben werden, denn so wird später sichergestellt, dass Nutzer\*innen nur auf die Daten im Territorium ihrer Orga zugreifen können.

Über die Tabelle 'user_settings' und 'settings' können neue Einstellungen mit default_value definiert werden und für einzelne Nutzer\*innen neu gesetzt werden. Hierbei kann man unterschiedliche Typen von Werten speichern (int,str,json).

In 'zones' können über eine geojson Datei Zonen eingelesen werden. In diesem Projekt gilt immer: Zone = Gemeinde.
Über 'territorries' und 'territorry_zones' können diese Zonen dann Territorien zugeordnet werden, welche widerum zu einer Orga gehören. So können größere Gebiete aus vielen Zonen angelegt und einer Orga zugeordnet werden.

### Drohnendaten
In der Tabelle 'drones' können Drohnen angelegt werden. Dies passiert im Anmeldeprozess einer Drohne über den /drones/signup/ API Endpunkt. 
'drone_update' und 'drone_event' enthalten die gesendeteten Drohnendaten. Hierbei ist ein Update ein eine Kombination aus Standort,Timestamp und Daten zur noch möglichen Flugdauer und Reichweite. 'drone_event' entgegen ist ein Ereignis bei dem eine Drohne entweder Feuer oder Rauch detektiert hat.

## API Docs
[kiwa.tech/api/docs](https://kiwa.tech/api/docs)

E-Mail: `admin@kiwa.tech` Passwort: `adminkiwa`

## main.py und ihre Umgebungsvariablen
In der main.py werden die nötigen Tabellen erstellt, Demodaten eingelesen und die Simulation gestartet. Das am Ende die gewünschten Daten in die Tabellen geschrieben werden, müssen die folgenden Umgebungsvariablen entsprechend gesetzt werden (für backend only in demo.env, ansonsten im [docker-compose.yml](https://github.com/waldbrandpraevention/frontend/blob/main/docker-compose.yml) des Frontends).

Benennung der Datenbankdatei und ihr Pfad.
```
DB_PATH = 'data/testing.db'
DB_BACKUP_PATH = 'data/backuptest.db'
```
Erstellen von Demo Accounts.
Im folgenden gilt:
Ist eine Varbiable nicht gesetzt, so wird das entsprechende Element nicht erstellt.
Will man nur einen User und eine Orga erstellen und dieser nur einen District zuordnen, so setzt man die Überflüssigen Variablen nicht.
```
ADMIN_MAIL = 'admin@kiwa.tech'
ADMIN_MAIL_TWO = 'ka@kiwa.tech'
ADMIN_PASSWORD = 'adminkiwa'
ADMIN_ORGANIZATION = 'KIWA'
ADMIN_ORGANIZATION_TWO = 'KIKA'
```
Für Demo Drohnenevents und -updates, können die folgenden Variablen gesetzt werden.
(unabhängig von der Simulation).
```
DEMO_LONG = '12.68895149'
DEMO_LAT = '52.07454738'
```
Mithilfe der folgenden Variablen, werden die Zonendaten gesetzt.
Unter (https://data.opendatasoft.com/explore/dataset/georef-germany-gemeinde%40public/table)
können geojson Files erstellt werden, die anschließend in die Datenbank eingelesen werden.
District entspricht "Kreis name" im geojson.
Sofern gesetzt, werden DEMO_DISTRICT (und DEMO_DISTRICT_TWO) der ADMIN_ORGANIZATION zugeordnet.
DEMO_DISTRICT_THREE wird ADMIN_ORGANIZATION_TWO zugeordnet, sofern beides gesetzt wurde.
```
GEOJSON_PATH = 'data/zone_data.geojson' 
DEMO_DISTRICT = 'Landkreis Potsdam-Mittelmark'
DEMO_DISTRICT_TWO = 'Landkreis Teltow-Fläming'
DEMO_DISTRICT_THREE = 'Landkreis Karlsruhe'
```

```
DOMAIN_API = 'http://127.0.0.1:8000'
EVENT_PATH = 'data/events' 
DRONE_FEEDBACK_PATH = 'data/feedback'
```
Simulationsspezifische Variablen.
```
RUN_SIMULATION = 'True'
SIMULATION_EVENT_CHANCE = '0.1'
SIMULATION_UPDATE_FREQUENCY = '10'
SIMULATION_DRONE_SPEED_MIN = '0.0001'
SIMULATION_DRONE_SPEED_MAX = '0.0002'
```

## Installation

 ---


  Um die vollständige Anwendung zu installieren, bitte die detaillierte [Readme im `waldbrandpraevention/frontend` Repo](https://github.com/waldbrandpraevention/frontend#readme) beachten.

--- 



## Development
#### Vorrausetzungen
- Python 3.10+
- https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2.md

*Anleitung getestet auf WSL/Ubuntu.*

[ 1 ] 
```
git clone https://github.com/waldbrandpraevention/backend.git
```
[ 2 ] 
```
cd waldbrandpraevention/backend
```
[ 3 ] 
```
pip install -r requirements.txt
```
[ 4 ] 
```
pip install python-dotenv
```
[ 5 ] 

 Spatialite installieren
https://www.gaia-gis.it/fossil/libspatialite/home
#### Windows
Auf Windows ein WSL nutzen.
#### Ubuntu / Debian / WSL
```
sudo apt install libspatialite7 libspatialite-dev libsqlite3-mod-spatialite
```
#### MacOS (nicht getestet)
```
brew install sqlite3 libspatialite
```
#### Alpine
```
apk add libspatialite=5.0.1-r5
```

[ 6 ]
TF2 Object detection installieren
https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2.md

[ 7 ] 

Bei Linux/MacOS muss noch in der `demo.env` die `\\` auf `/` geändert werden.

Eventuell vorhandene Datenbank löschen `rm -f testing.db`

[ 8 ]
```
uvicorn main:app --reload --env-file demo.env
```
Backend läuft auf http://localhost:8000<br>
API Documentation auf http://localhost:8000/docs

#### Tools

Spatialite GUI Editor https://www.gaia-gis.it/fossil/spatialite_gui/index

QGIS GUI https://www.qgis.org/de/site/about/index.html
