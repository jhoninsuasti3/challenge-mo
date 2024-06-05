# Django project Payments - Wearemo

# Instructions to use

## Installation

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt`
```

## Docker: Run Project

### Run container

```
docker build -t django-base-ms .
docker-compose up --force-recreate --build
```

### Run tests

```
Terminal 1:
docker-compose up

Terminal 2:
docker-compose exec api bash
python -m pytest
```

---

## Run pre-commit

pre-commit run --all-files

## Docker-compose validate coverage

docker-compose -f docker-compose.testing.yml up --force-recreate --build
docker-compose -f docker-compose.testing.yml run --rm api-total sh -c "pytest -vv"

uvicorn api.main:app --host 0.0.0.0 --port 8001

alembic revision --autogenerate -m "generate models"

## Generate documentation

http:localhost:8000/swagger
http:localhost:8000/redoc

## Docker-compose execute test

docker-compose -f docker-compose.testing.yml up --force-recreate --build
docker-compose -f docker-compose.testing.yml run --rm api sh -c "pytest -vv"
