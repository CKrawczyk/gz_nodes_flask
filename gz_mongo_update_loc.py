#This script will go through the mongo database for galaxy zoo
#and add a `location` field that sifts the [RA,DEC] to an earth
#like [log,lat] system (-180,180) not (0,360)
#this field can be used to index the database the right way

from pymongo import MongoClient
import progressbar as pb

client=MongoClient('localhost',27017)
db=client['galaxy_zoo']
subjects=db['galaxy_zoo_subjects']

widgets = ['Update: ', pb.Percentage(), ' ', pb.Bar(marker='0',left='[',right=']'),' ', pb.ETA()]
pbar = pb.ProgressBar(widgets=widgets, maxval=subjects.count())
pbar.start()
ct=0
for s in subjects.find({}):
    #loop over all subjects
    coord=s['coords']
    s[u'location_geo']= {u'type':u'Point', u'coordinates': [coord[0]-180,coord[1]]}
    subjects.update({'_id':s['_id']}, {'$set': s}, upsert=False)
    pbar.update(ct)
    ct+=1
pbar.finish()
