from flask import Flask, jsonify, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from gz_classes import *
from gz_mongo import *

application = Flask(__name__, instance_relative_config=True)
#application.config.from_pyfile('gz_nodes_local.cfg', silent=True)
application.config.from_envvar('APPLICATION_SETTINGS', silent=True)

db=SQLAlchemy(application)
db.Model.metadata.reflect(db.get_engine(application,'gz2'))
BC2=get_tables(db,'gz2')
db.Model.metadata.reflect(db.get_engine(application,'gz3'),extend_existing=True)
BC3=get_tables(db,'gz3')
db_dict={'gz2':GZ2(db,application,BC2),
               'gz3':GZ3(db,application,BC3),
               'gz4_s':GZ4_sloan(),
               'gz4_u':GZ4_ukidss(),
               'gz4_f':GZ4_ferengi(),
               'gz4_c':GZ4_candels()}

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/_get_path')
def get_path():
    table = request.args.get('table', 'gz2', type=str)
    argv = request.args.get('argv', '180 0', type=str)
    return jsonify(result=db_dict[table].run(argv))

if __name__=="__main__":
    #application.debug = True
    #application.run()
    application.run(host='0.0.0.0',port=80)
