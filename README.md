<h1 align="center">Waldbrandprävention Backend</h1>
<p align="center">   
    <img width="460" height="300" src="https://bp.adriansoftware.de/logos/logo-v1.svg?ref=gh-back"> <!-- Todo make file local -->
</p>

<div align="center">

[![pylint](https://img.shields.io/github/workflow/status/waldbrandpraevention/backend/Pylint?style=for-the-badge)](https://github.com/waldbrandpraevention/backend/actions/workflows/Pylint.yml)
![](https://img.shields.io/github/commit-activity/m/waldbrandpraevention/backend?style=for-the-badge)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)



</div>

## Deployment mit Docker

Siehe [Readme im `waldbrandpraevention/frontend` Repo](https://github.com/waldbrandpraevention/frontend).

## Development

Python backend mit Fastapi

Python Dependencies:
- fastapi: api stuff
- python-jose: jwt stuff
- passlib: hashing
- uvicorn: server

1. GitHub Repo clonen
```
git clone https://github.com/waldbrandpraevention/backend.git
```
2. Docker Image erstellen
```
TODO
```
3. Docker Container starten
```
TODO
```

Starten ohne Docker
```
cd waldbrandpraevention/backend
uvicorn main:app --reload
```

```
Backend läuft auf http://localhost:8000
```

```
API Documentation auf http://localhost:8000/docs
```
