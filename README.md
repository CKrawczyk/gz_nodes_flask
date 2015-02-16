[![Build Status](http://img.shields.io/badge/Built%20at-%23dotastro-blue.svg?style=flat)](http://dotastronomy.com/six/)

gz_nodes_flask
============

Galaxy Zoo visualization using a node tree
The node tree is made using d3 and js.

This app is built using Flask and Flask-PyMongo to connect to a
Mongo database. The `instance/gz_nodes.cfg` file should contain the
information needed to connect to the database:

```
MONGO_HOST = 'localhost'
MONGO_DBNAME = 'galaxy_zoo'
```

*NOTE 1*: If using docker set `MONGO_HOST` to the result of `ip route
 show 0.0.0.0/0 | grep -Eo 'via \S+' | awk '{ print $2 }'`. If using
 boot2docker set host to `192.168.59.3`. 

*NOTE 2*: If running via `python routs.py` (i.e. not using docker) place the above in
`instance/gz_nodes_local.cfg`. This allows independent setups
for running local and running through docker.

The Mongo database used is a cobination of Galaxy Zoo 2, 3, and 4. The GZ2
and GZ3 data has been converted from the SQL source database, and all subjects
have been modified and indexed for faster queries.

Docker is set up to run the flask app on an internal Apache/mod_wsgi server.
See http://blog.dscpl.com.au/2014/12/hosting-python-wsgi-applications-using.html for more info.

##Run using fig
```
fig build
fig up
```
Navigate to `http://localhost:5000/` (docker) or
`http://192.168.59.103:5000/` (boot2docker) in a web browser.


##Run using docker
```
./gz_build.sh
./gz_up.sh
```
Navigate to `http://localhost:5000/` (docker) or
`http://192.168.59.103:5000/` (boot2docker) in a web browser.

##Run local
```
python routs.py
```
Navigate to `http://localhost:5000` in a web browser.

##Node tree properties
The nodes can be moved by dragging them around and be collapsed by
clicking on them. Clicking a second time will re-expand the nodes.
The nodes will try to arrange themselves so the ones with the most votes
are on top.

There are 3 sliders at the bottom that can be used to adjust the tree:
+ `Charge`: How much the nodes repel each other
+ `Link Strength`: How stretchy the links are
+ `Friction`: How damped the motion is

The `Reset` button will set all the sliders back to their default position.
