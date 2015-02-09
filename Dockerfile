FROM grahamdumpleton/mod-wsgi-docker:python-2.7-onbuild
RUN pip install --allow-external mysql-connector-python mysql-connector-python
CMD ["gz_nodes_wsgi.py"]