#this script will convert the GZ2 and GZ3 classifications databases from SQL to mongo
from pymongo import MongoClient
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import progressbar as pb

client=MongoClient('localhost',27017)
db=client['galaxy_zoo']
classifications_mongo=db['galaxy_zoo_classifications']
subjects_mongo=db['galaxy_zoo_subjects']

engine2=create_engine('mysql+mysqlconnector://docker:docker@localhost/gz2')
s2="""SELECT group_concat(a.answer_id order by a.id asc) as vote_path, b.name, c.user_id
	FROM 
		annotations a 
        join asset_classifications ac on a.classification_id = ac.classification_id
        join assets b on ac.asset_id=b.id
        join classifications c on c.id = ac.classification_id
	where a.classification_id=%i;"""

widgets = ['Update: ', pb.Percentage(), ' ', pb.Bar(marker='0',left='[',right=']'),' ', pb.ETA()]

max_id=16499351
pbar = pb.ProgressBar(widgets=widgets, maxval=max_id)
pbar.start()
for i in xrange(1,max_id+1):
    t=engine2.execute(s2%i).fetchall()[0]
    if t[0] is not None:
        C={
            u'annotations': map(int,t[0].split(',')),
            u'user_id_sql': t[2],
            u'subject_ids': subjects_mongo.find_one({'zooniverse_id':t[1]})['_id'],
            u'classification_id_sql': i
            }
        #classifications_mongo.insert(C)
        #had to restart due to low disk space, upsert to add 'classification_id_sql' to each document and finish the rest
        classifications_mongo.update({'user_id_sql': C['user_id_sql'],'subject_ids': C['subject_ids'], 'annotations': C['annotations']}, C, upsert=True)
    pbar.update(i)
pbar.finish()

engine3=create_engine('mysql+mysqlconnector://docker:docker@localhost/gz3')
s3="""SELECT group_concat(a.answer_id order by a.id asc) as vote_path, b.zooniverse_id, c.zooniverse_user_id
    FROM
        annotations a
        join asset_classifications ac on a.classification_id = ac.classification_id
        join classifications c on c.id = ac.classification_id
        join assets b on ac.asset_id = b.id
    WHERE a.classification_id=%i;"""

max_id=9902592
pbar = pb.ProgressBar(widgets=widgets, maxval=max_id)
pbar.start()
for i in xrange(1,max_id+1):
    t=engine3.execute(s3%i).fetchall()[0]
    if t[0] is not None:
        C={
            u'annotations': map(int,t[0].split(',')),
            u'user_id_sql': t[2],
            u'subject_ids': subjects_mongo.find_one({'zooniverse_id':t[1]})['_id'],
            u'classification_id_sql': i
            }
        classifications_mongo.insert(C)
    pbar.update(i)
pbar.finish()
