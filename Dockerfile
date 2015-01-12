FROM python:2-onbuild
RUN pip install -r requirements.txt
RUN pip install --allow-external mysql-connector-python mysql-connector-python
EXPOSE 80
CMD python routs.py