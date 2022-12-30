# jumble

Python implementation of the classic scrambled word game


# Setup

## First time database creation

- make sure to fill relevant information in .env file for DB creation
  ```
  POSTGRES_USER=#####
  POSTGRES_PASSWORD=#####
  POSTGRES_DATABASE_NAME=jumble-db # chosen db name
  POSTGRES_IP=localhost:#### # connect to db using psql and type `\conninfo`
  ```
- excecute the script under `jumble/database.py` to create the db.
- create tables using `alembic`
  - initialise alembic `alembic init alembic`
  - edit the `alembic/env.py` file:
    - update `target_metadata` to use the models created
    - add line `config.set_main_option("sqlalchemy.url", os.environ["POSTGRES_DATABASE_URL"])` to tell alembic how to connect to db
  - finally run the following cmd to create all tables
  ```
  alembic revision --autogenerate -m "added tables"
  ```
  - double check the created revision under `alembic/versions`
