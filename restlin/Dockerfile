FROM python:latest

EXPOSE 1337

WORKDIR /code

COPY requirements.txt /code/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY config.config /config/
COPY src/database/database.py /code/src/database/
COPY src/models/* /code/src/models/
COPY src/logger/logger.py /code/src/logger/
COPY src/restlin.py /code/src/

CMD python3 src/restlin.py 
