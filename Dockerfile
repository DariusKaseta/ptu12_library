# syntax=docker/dockerfile:1
FROM python:slim-bullseye
WORKDIR /app
COPY ./ptu12_library .
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
