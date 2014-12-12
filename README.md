![Build Status](http://img.shields.io/badge/Built%20at-%23dotastro-blue.svg?style=flat)

gz_nodes_flask
============

Galaxy Zoo visualization using a node tree

The node tree is made using d3 and js.

This app is built using flask and flask-sqlalchemy to connect to a
MySQL database. The `instance/gz_nodes.cfg` file should contain the
information needed to connect to the database (with databases named `gz2` and `gz3`):

`SQLALCHEMY_DATABASE_URI =mysql+mysqlconnector://username:password@host:port/gz2`
`SQLALCHEMY_BINDS = {'gz2': mysql+mysqlconnector://username:password@host:port/gz2, 'gz3': mysql+mysqlconnector://username:password@host:port/gz3`

To run locally `python routs.py` and navigate to `http://127.0.0.1:5000/` in a web browser.

The nodes can be moved by dragging them around and be collapsed by
clicking on them. Clicking a second time will re-expand the nodes.
The nodes will try to arrange themselves so the ones with the most votes
are on top.

There are 3 sliders at the bottom that can be used to adjust the tree:
+ `Charge`: How much the nodes repel each other
+ `Link Strength`: How stretchy the links are
+ `Friction`: How damped the motion is

The `Reset` button will set all the sliders back to their default position.
