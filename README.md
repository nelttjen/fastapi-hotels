# Hotel service

## Description
The goal of the project is to provide an interface for user
to create bookings of the hotel's free rooms. 
Also, there's an admin panel to manage all the existing data. <br>

---
# Installation
## Technical information

<ul>
<li>General: Python 3.10.6, FastAPI, Docker</li>
<li>Databases: PostgreSQL, MongoDB</li>
<li>Tests: PyTest</li>
<li>Admin panel: sqladmin</li>
<li>Authorization: Client-Side JWT Tokens</li>
</ul>

## Requirements
<ul>
<li>Python 3.10.6 <a href="https://www.python.org/downloads/release/python-3106/">Download</a></li>
<li>Docker <a href="https://www.python.org/downloads/release/python-3106/">Download</a></li>
</ul>

## Configuring project

1. Clone repository: 
```bash
git clone https://github.com/nelttjen/fastapi-hotels.git
```
2. Create .env file by using .env-example template (preferred)
```bash
cp -f .env.example .env
```
or make a new file and fill data manually
```bash
touch .env
```
3. Build docker containers (docker compose required)
```bash
# dev version (Need to run server and migrations manually)
sudo docker compose -f docker-compose.yaml build
```
```bash
# prod version (requires .env-prod file)
cp .env .env-prod
sudo docker compose -f docker-compose-prod.yaml build
```
4. Run containers
```bash
# dev version
sudo docker compose -f docker-compose.yaml up
```
```bash
# prod version (requires .env-prod file)
sudo docker compose -f docker-compose-prod.yaml up
```
---
## Development server
In the dev version of docker you need to manually run migrations and server
1. Create venv, install dependencies
```shell
sudo apt install python3-dev python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip3 install poetry
poetry install
```
2. run migrations and dev server
```shell
poetry run alembic upgrade head
poetry run uvicorn main:app --reload
```