[![Build Status](http://img.shields.io/badge/Built%20at-%23dotastro-blue.svg?style=flat)](http://dotastronomy.com/six/)

gz_nodes_flask
============

Galaxy Zoo visualization using a node tree

The node tree is made using d3 and js.

This app is built using flask and flask-sqlalchemy to connect to a
MySQL database. The `instance/gz_nodes.cfg` file should contain the
information needed to connect to the database (with databases named `gz2` and `gz3`):

```
SQLALCHEMY_DATABASE_URI =mysql+mysqlconnector://username:password@host:port/gz2
SQLALCHEMY_BINDS ={'gz2':mysql+mysqlconnector://username:password@host:port/gz2,
                                     'gz3':mysql+mysqlconnector://username:password@host:port/gz3}
```

*NOTE*: If using docker set host to the result of `"ip route
 show 0.0.0.0/0 | grep -Eo 'via \S+' | awk '{ print \$2 }'"`. If using
 boot2docker set host to `192.168.59.3`. In either case make sure
 mysql is set up to accept connections from `username` on this host
 address (see
 http://stackoverflow.com/questions/1559955/host-xxx-xx-xxx-xxx-is-not-allowed-to-connect-to-this-mysql-server
 for more info on how to do this).

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

The nodes can be moved by dragging them around and be collapsed by
clicking on them. Clicking a second time will re-expand the nodes.
The nodes will try to arrange themselves so the ones with the most votes
are on top.

There are 3 sliders at the bottom that can be used to adjust the tree:
+ `Charge`: How much the nodes repel each other
+ `Link Strength`: How stretchy the links are
+ `Friction`: How damped the motion is

The `Reset` button will set all the sliders back to their default position.
