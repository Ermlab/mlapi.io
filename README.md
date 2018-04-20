MLAPI.IO
========

Machine learning API framework, check out https://mlapi.io

# Developer documentation

If you want to host your own ml api with use of mlapi, check out our documentation page.

https://ermlab.github.io/mlapi.io/


# Installation

## Dockerfile

```bash
docker build -t mlapi .
docker run -d --name mlapi -e APP_SETTINGS=DevelopmentConfig -e DB_SECRET_KEY=extremely_secret_key -p 0.0.0.0:8000:8000 mlapi gunicorn -b 0.0.0.0:8000 mlapi.app
docker exec -d mlapi bash -c "python manage.py create_db"
```
Then the API is available at `localhost:8000`.


## Manual installation
### Seeting up the environment

```bash
virtualenv -p python3 .venv
source .venv/bin/activate
pip install -r requirements.txt

export DB_SECRET_KEY=extremely_secret_key
python manage.py create_db
```
For ease of use the `DB_SECRET_KEY` value can be written inside `API/db/config.py`.
Then you will need to create the first DB admin user which then will allow you to create other users via API rather than using the command-line and direct DB connection. 
```python
python
> from mlapi.app import database as db
> from db.dbModels import User
> admin = User(email="test@test.test", password="secret_admin_password", uses=1000, is_admin=True)
> db.session.add(admin)
> db.session.commit()
> exit()
```

## Usage

```bash
source .venv/bin/activate
DB_SECRET_KEY=extremely_secret_key gunicorn mlapi.app
```
If you want the server to restart on every code change just add a `--reload` parameter after `gunicorn` in the last command.

## Communication with API

Basic tips on how to communicate with the API can be found [here](https://mlapi.io/category/api/).
Of course, the address to communicate with your local instance will be `localhost:8000`.
