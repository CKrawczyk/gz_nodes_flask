#this script will convert the GZ2 and GZ3 asset databases from SQL to mongo
from pymongo import MongoClient
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import progressbar as pb
from random import random

client=MongoClient('localhost',27017)
db=client['galaxy_zoo']
subjects_mongo=db['galaxy_zoo_subjects']


Base2=automap_base()
engine2=create_engine('mysql+mysqlconnector://docker:docker@localhost/gz2')
Base2.prepare(engine2,reflect=True)
session2=Session(engine2)
BC2=Base2.classes

widgets = ['Update: ', pb.Percentage(), ' ', pb.Bar(marker='0',left='[',right=']'),' ', pb.ETA()]

a2=session2.query(BC2.assets)
pbar = pb.ProgressBar(widgets=widgets, maxval=a2.count())
pbar.start()
ct=0
for a in a2:
    A={
        u'classification_count': a.classification_count,
        u'coords': [float(a.ra),float(a.dec)],
        u'location_geo': {u'type':u'Point', u'coordinates': [float(a.ra)-180,float(a.dec)]},
        u'location': {u'standard': a.location},
        u'metadata': {
            u'survey': u'GZ2',
            u'redshift_bin': a.redshift_bin,
            u'magsize_bin': a.magsize_bin,
            u'battle_bin': a.battle_bin,
            u'stripe82': a.stripe82,
            u'stripe82_coadd': a.stripe82_coadd,
            u'extra_original': a.extra_original,
            u'external_ref': a.external_ref,
            u'region': a.region
            },
        u'zooniverse_id': a.name,
        u'random': random()
        }
    #not all sdssid's are unique :(, use update with upsert to only use the most recent version of each subject
    subjects_mongo.update({'zooniverse_id': a.name}, A, upsert=True)
    #subjects_mongo.insert(A)
    pbar.update(ct)
    ct+=1
pbar.finish()

engine3=create_engine('mysql+mysqlconnector://docker:docker@localhost/gz3')

a3=engine3.execute("select * from assets")
cols=['id', 'name', 'project_id', 'created_at', 'updated_at', 'location', 'classification_count', 'external_ref', 'average_score', 'active', 'workflow_id', 'ra', 'dec', 'battle_bin', 'inverted_location', 'thumbnail_location', 'redshift', 'zooniverse_id', 'magnitude', 'magnitude_error', 'radius', 'cutout_size', 'radius_error', 'absolute_magnitude', 'absolute_radius']

def HST_split(s):
    if s is None:
        return None
    s=s[5:]
    s=s.replace('"','')
    T=dict([tuple(s1.split(':')) for s1 in s.split('\n')[:-1]])
    return {k: float(v) for k,v in T.iteritems()}

def HST_split2(s):
    if s is None:
        return None
    s=s[6:]
    s=s.replace('"','')
    s=s.replace('\n:','\n')
    T=dict([tuple(s1.split(':')) for s1 in s.split('\n')[:-1]])
    return {k: float(v) for k,v in T.iteritems()}

def clean_dict(d):
    return {k: v for k, v in d.iteritems() if v}

pbar = pb.ProgressBar(widgets=widgets, maxval=a3.rowcount)
pbar.start()
ct=0
for r in a3:
    a=dict(zip(cols,r))
    meta= {
        u'survey': u'Hubble',
        u'redshift': a['redshift'],
        u'magnitude': HST_split(a['magnitude']),
        u'radius': HST_split(a['radius']),
        u'Hubble_id': a['name'],
        u'absolute_magnitude': HST_split2(a['absolute_magnitude']),
        u'absolute_radius': HST_split2(a['absolute_radius']),
        u'battle_bin': a['battle_bin']
        }
    A=clean_dict({
        u'classification_count': a['classification_count'],
        u'coords': [float(a['ra']),float(a['dec'])],
        u'location_geo':  {u'type':u'Point', u'coordinates': [float(a['ra'])-180,float(a['dec'])]},
        u'location': {
            u'standard': a['location'],
            u'thumbnail': a['thumbnail_location'],
            u'inverted': a['inverted_location']
            },
        u'metadata': clean_dict(meta),
        u'zooniverse_id': a['zooniverse_id'],
        u'random': random()
        })
    subjects_mongo.insert(A)
    pbar.update(ct)
    ct+=1
pbar.finish()
