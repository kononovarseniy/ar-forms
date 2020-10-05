FROM python:3.8

RUN useradd -r uwsgi && mkdir -p /srv/ar-forms && chown -R uwsgi:uwsgi /srv/ar-forms
WORKDIR /srv/ar-forms
EXPOSE 48784

COPY uwsgi.ini ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

USER uwsgi

CMD ["uwsgi", "--ini", "uwsgi.ini"]

