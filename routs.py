from flask import Flask, jsonify, render_template, request
from flask.ext.pymongo import PyMongo
from gz_mongo import *

application = Flask(__name__, instance_relative_config=True)

#check if the app is running local (not docker)
if __name__=="__main__":
    application.config.from_pyfile('gz_nodes_local.cfg', silent=True)
else:
    application.config.from_envvar('GZ_NODES_SETTINGS', silent=True)
mc = PyMongo(application)

db_dict={'gz2':GZ2(mc),
               'gz3':GZ3(mc),
               'gz4_s':GZ4_sloan(mc),
               'gz4_u':GZ4_ukidss(mc),
               'gz4_f':GZ4_ferengi(mc),
               'gz4_c':GZ4_candels(mc)}

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/_get_path')
def get_path():
    table = request.args.get('table', 'gz2', type=str)
    argv = request.args.get('argv', '180 0', type=str)
    return jsonify(result=db_dict[table].run(argv))

if __name__=="__main__":
    application.debug = True
    application.run()
