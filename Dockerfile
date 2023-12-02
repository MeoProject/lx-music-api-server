FROM python:3.10.13-slim-bullseye

WORKDIR /app

COPY . /app

RUN pip install --no-cache -r requirements.txt

CMD [ "python", "main.py" ]