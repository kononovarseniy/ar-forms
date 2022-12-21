## ArFroms
TODO: description

### Installation with docker
To install ArForms using docker you need to install docker-compose.
After you have installed docker run the following commands in the project directory:
```
# Create self-signed SSL certificate
mkdir certs
openssl req -x509 -newkey rsa:4096 -nodes -keyout certs/ar-forms.key -out certs/ar-forms.crt
# Build docker images
docker-compose build
```
To run server use ```docker-compose start```



### Installation without docker
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
`pip intall -r ar-forms/requirements.txt`

#### Web server
Set up any web-server with wsgi support (we use nginx).
Start nginx and uwsgi.
