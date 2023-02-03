<h1 align="center">Waldbrandprävention Backend</h1>
<p align="center">   
    <img width="320" height="160" src="https://bp.adriansoftware.de/media/logo-v1.svg?ref=gh-back"> <!-- Todo make file local -->
</p>

<div align="center">

[![pylint](https://img.shields.io/github/actions/workflow/status/waldbrandpraevention/backend/pylint.yml?branch=main&style=for-the-badge&label=ci)](https://github.com/waldbrandpraevention/backend/actions/workflows/Pylint.yml)
![](https://img.shields.io/github/actions/workflow/status/waldbrandpraevention/backend/docker-image.yml?branch=main&style=for-the-badge&label=docker)
![](https://img.shields.io/github/commit-activity/m/waldbrandpraevention/backend?style=for-the-badge&label=commits)
![](https://img.shields.io/docker/image-size/waldbrandpraevention/backend?style=for-the-badge&label=image&color=orange)
[![](https://img.shields.io/codefactor/grade/github/waldbrandpraevention/backend?style=for-the-badge)](https://www.codefactor.io/repository/github/waldbrandpraevention/backend/issues/main)


![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)


</div>

## Installation

 ---


  Um die vollständige Anwendung zu installieren, bitte die detaillierte [Readme im `waldbrandpraevention/frontend` Repo](https://github.com/waldbrandpraevention/frontend#readme) beachten.

--- 



## Development
#### Vorrausetzungen
- Python 3.10+

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
##### Windows
???
##### Ubuntu / Debian / WSL
```
sudo apt install libspatialite7 libspatialite-dev libsqlite3-mod-spatialite
```
##### MacOS (nicht getestet)
```
brew install sqlite3 libspatialite
```
##### Alpine
```
apk add libspatialite=5.0.1-r5
```

[ 6 ] 

Bei Linux/MacOS muss noch in der `demo.env` die `\\` auf `/` geändert werden.

Eventuell vorhandene Datenbank löschen `rm -f testing.db`

[ 7 ]
```
uvicorn main:app --reload --env-file demo.env
```
Backend läuft auf http://localhost:8000<br>
API Documentation auf http://localhost:8000/docs

