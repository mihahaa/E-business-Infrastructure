FROM python:3

RUN mkdir -p /opt/src/customer
WORKDIR /opt/src/customer

COPY store/customerapplication.py ./customerapplication.py
COPY store/configuration.py ./configuration.py
COPY store/models.py ./models.py
COPY store/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/customer"

ENTRYPOINT ["python", "./customerapplication.py"]