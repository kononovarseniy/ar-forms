FROM postgres
EXPOSE 5432

RUN mkdir -p /etc/postgresql/ && cp /usr/share/postgresql/postgresql.conf.sample /etc/postgresql/postgresql.conf
COPY init.sh /docker-entrypoint-initdb.d/

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]

