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

## Installation

> Die folgende Anleitung beschreibt nur das Deployen des Backends. Um die vollständige Anwendung zu installieren, bitte die detaillierte [Readme im `waldbrandpraevention/frontend` Repo](https://github.com/waldbrandpraevention/frontend#readme) ansehen.

1. GitHub Repo clonen
```
git clone https://github.com/waldbrandpraevention/frontend.git
```
2. Docker Image erstellen
```
cd frontend && docker build -f Dockerfile.withNginx -t wb-frontend .
```
3. Docker Container starten
```
docker run --rm -it -p 8080:80 wb-frontend
```
4. Backend läuft auf http://localhost:8080

## Development

// todo

