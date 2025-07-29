# CERC Persistence

The persistence package includes classes to store different class objects in a Postgres database.

## Models

This defines models for all class objects that we want to persist. It is used for Object Relation Mapping (ORM)
of the class objects to database table columns

## Repositories

This defines repository classes that contain CRUD methods for database operations. The constructor of all repositories
requires the database name to connect to and the application environment (PROD or TEST). Tests use a different database
from the production environment, which is why this is necessary. An example is shown below:

```python
from cerc_persistence.db_setup import DBSetup

# instantiate city repo for hub production database
db = DBSetup(db_name='hub', app_env='PROD', dotenv_path='/path/to/.env', admin_password='application_password', application_uuid='UUID')
```

All database operations are conducted with the production database (*PROD*) named *hub* in the example above.

## config_db

This Python file is a configuration class that contains variables that map to configuration parameters in a .env file.
It also contains a method ``def conn_string()`` which returns the connection string to a Postgres database.

## Base

This class has a constructor that establishes a database connection and returns a reference for database-related CRUD
operations.

## Database Configuration Parameter

A .env file (or environment variables) with configuration parameters described below are needed to establish a database
connection:

```
# production database credentials
PROD_DB_USER=postgres-database-user
PROD_DB_PASSWORD=postgres-database-password
PROD_DB_HOST=database-host
PROD_DB_PORT=database-port

# test database credentials
TEST_DB_USER=postgres-database-user
TEST_DB_PASSWORD=postgres-database-password
TEST_DB_HOST=database-host
TEST_DB_PORT=database-port
```

## Database Related Unit Test

Unit tests that involve database operations require a Postgres database to be set up.
The tests connect to the database server using the default postgres user (*postgres*).
NB: You can provide any credentials for the test to connect to postgres, just make sure
the credentials are set in your .env file as explained above in *Database Configuration Parameters* section.

When the tests are run, a **test_db** database is created and then the required tables for
the test. Before the tests run, the *test_db* is deleted to ensure that each test starts
on a clean slate.
