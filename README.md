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

The `Upload` button allows the user to upload a `.csv` file containing
a list of galaxies to explore. The file should be formeted as:

```
value,table
180 90,gz2
587733609628696658,gz2
588011502072234044,gz2
15.768 0.474,gz2
136.145 14.593,gz2
AHZ20003km,gz3
AHZ6000bvu,gz3
AGZ0002m46,gz4_s
AGZ0003diy,gz4_s
AGZ00014r1,gz4_s
AGZ0004v0i,gz4_s
AGZ00000s3,gz4_c
AGZ0006ry1,gz4_u
AGZ0007te4,gz4_f
AGZ0007to6,gz4_f
```

The value column can be an RA DEC pair seperated by a space, or the
`Zooniverse_id` (*NOTE*: for GZ2 the `Zooniverse_id` is the SDSS id). 
The table column can be

```
gz2
gz3
gz4_s
gz4_c
gz4_u
gz4_f
```
to indicate what Galaxy Zoo table to search.

*NOTE*: Make sure there are no spaces around the `,` or the script
will not read in the file correctly.

*NOTE*: Keep uploaded file sizes below ~35 KB (~2000 rows) to avoid
freezing your browser. All file reading/parsing is handeled in client size js.
