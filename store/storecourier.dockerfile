FROM python:3

RUN mkdir -p /opt/src/courier
WORKDIR /opt/src/courier

COPY store/courierapplication.py ./courierapplication.py
COPY store/configuration.py ./configuration.py
COPY store/models.py ./models.py
COPY store/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/courier"

ENTRYPOINT ["python", "./courierapplication.py"]
