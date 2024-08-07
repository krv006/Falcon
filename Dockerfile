FROM python:3.11-slim

WORKDIR /app
COPY  . /app

RUN #pip3 install -r requirements.txt

RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip install -r requirements.txt

#RUN chmod +x entrypoint

#CMD ["./entrypoint"]

CMD ["python3", "manage.py", "runserver", "0:8000"]