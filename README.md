## ArFroms
TODO: description

### Installation
#### PostgreSQL
This application uses PostgreSQL, so you need to install and configure it.\
To create database for this project run execute following commands in `psql`:
```
CREATE DATABASE ar_forms;
CREATE USER ar_forms WITH ENCRYPTED PASSWORD 'master';
GRANT ALL PRIVILEGES ON DATABASE ar_forms TO ar_forms;
\c ar_forms
CREATE EXTENSION pgcrypto;
```

#### Virtual environment
If you wish, you can create virtual environment for project:\
`python -m venv .venv`\
To activate it execute:\
`source .venv/bin/activate`

#### Dependencies
To install dependencies using pip, execute following command:\
`pip intall -r requirements.txt`

#### Web server
Set up any web-server with wsgi support (we use nginx).
Start nginx and uwsgi.
