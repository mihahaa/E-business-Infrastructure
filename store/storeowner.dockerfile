FROM python:3

RUN mkdir -p /opt/src/owner
WORKDIR /opt/src/owner

COPY store/ownerapplication.py ./ownerapplication.py
COPY store/configuration.py ./configuration.py
COPY store/models.py ./models.py
COPY store/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/owner"

ENTRYPOINT ["python", "./ownerapplication.py"]