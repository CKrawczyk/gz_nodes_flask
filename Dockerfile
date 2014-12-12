FROM python:2-onbuild
RUN pip install --allow-external mysql-connector-python mysql-connector-python
