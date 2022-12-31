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

  ## Connecting to CloudSQL

  TO create an instance on to cloud SQL, go to gcp console UI - SQL section, and create a DB with the following properties"
  - instanceID=$POSTGRES_DATABASE_NAME
  - root-password=$POSTGRES_PASSWORD
  - database-version=POSTGRES_14
  - region=$LOCATION
  - connections:
    - Private IP
    - default network
    - Allocated IP range: Use automatically assigned IP range

Refering to variables as defined in the .env file.

Get the IP address of newly created instance running
```
gcloud sql instances describe $POSTGRES_DATABASE_NAME | grep ipAddress
```

Finally create a db inside the instance running (we make teh chocie here to name the db same as instance on cloudSQL):
```
gcloud sql databases create $POSTGRES_DATABASE_NAME --instance=$POSTGRES_DATABASE_NAME
```
