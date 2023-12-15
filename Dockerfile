FROM python:3.10-alpine

WORKDIR /app

COPY ./main.py .
COPY ./common ./common
COPY ./modules ./modules
COPY ./requirements.txt .

# ........., ....................., ......................

RUN pip install --no-cache-dir  -r requirements.txt

CMD [ "python", "main.py" ]
