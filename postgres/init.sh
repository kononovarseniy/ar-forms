#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ar_forms;
    CREATE USER ar_forms WITH ENCRYPTED PASSWORD 'master';
    GRANT ALL PRIVILEGES ON DATABASE ar_forms TO ar_forms;
    \c ar_forms
    CREATE EXTENSION pgcrypto;
EOSQL
