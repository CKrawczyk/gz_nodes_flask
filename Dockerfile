FROM google/python
ADD . /usr/src/app/
WORKDIR /usr/src/app/
RUN pip install -r requirements.txt
RUN pip install --allow-external mysql-connector-python mysql-connector-python
EXPOSE 80
CMD ./run_flask.sh