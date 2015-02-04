from pymongo import MongoClient
from pprint import pprint
import re
from random import random
import gz4_sloan_ukidss as sloan_ukidss
import gz4_ferengi as ferengi
import gz4_candels as candels

client=MongoClient('localhost', 27017)
db=client['galaxy_zoo']
subjects=db['galaxy_zoo_subjects']
classifications=db['galaxy_zoo_classifications']

class GZ4_base:
    def __init__(self):
        self.survey_name=''
        self.survey=None
        self.debug=False
        self.anything_odd=''
    def get_rand_obj(self):
        s=subjects.find_one({'metadata.survey':self.survey_name, 'random':{'$gt':random()}})
        return s['zooniverse_id'],s['_id'],s['coords'][0],s['coords'][1],s['location']['standard']       
    def get_links(self,m_id):
        #m_id is the mongo "_id" value for the galaxy subject
        #find all classifications with the propper subject id
        c=classifications.find({'subject_ids':m_id})
        vote_dict={}
        odd_dict={}
        for i in c:
            votes=[0]
            for j in i['annotations']:
                vote=j.items()[0]
                if (vote[0]==self.anything_odd) and (not isinstance(vote[1],list)):
                    vote=(vote[0],[vote[1]])
                if isinstance(vote[1],list):
                    #this is the answer to "anything odd"
                    for k in vote[1]:
                        if (k[0]=='x') or (self.survey_name=='candels'):
                            key=self.survey.convert[k]
                            odd_dict[key]=odd_dict.get(key,0)+1
                else:
                    if vote[0] not in ['lang','user_agent']:
                        votes.append(self.survey.convert[vote])
            if self.debug:
                print votes,self.survey.valid_path(votes)
            if self.survey.valid_path(votes):
                votes=[v for v in votes if v!=-1]
                for key in zip(votes[:-1],votes[1:]):
                    vote_dict[key]=vote_dict.get(key,0)+1
        odd_list=map(list,odd_dict.items())
        if self.debug:
            print odd_list
        odd_list.sort(key=lambda x: x[1])
        odd_list=odd_list[::-1]
        self.odd_list=[{'name':k[0], 'value':k[1]} for k in odd_list]
        self.links=[{'source':k[0], 'target':k[1], 'value': v} for k,v in vote_dict.iteritems()]        
    def run(self,argv='180 0'):
        if argv=='random':
            s=subjects.find_one({'metadata.survey':self.survey_name, 'random':{'$gt':random()}})
        else:
            argv=re.findall(r"[\w.-]+",argv)
            L=len(argv)
            if L==1:
                s=subjects.find_one({'zooniverse_id':argv[0]})
            else:
                ra,dec=map(float,argv)
                s=subjects.find_one({'coords':{'$near':[ra,dec]}, 'metadata.survey':self.survey_name})
        if self.debug:
            pprint(s)
        self.get_links(s['_id'])
        return {'nodes':self.survey.nodes,'links':self.links,'image_url':s['location']['standard'],'ra':s['coords'][0],'dec':s['coords'][1],'gal_name':s['zooniverse_id'],'odd_list':self.odd_list}
    
class GZ4_sloan(GZ4_base):
    def __init__(self,debug=False):
        self.debug=debug
        self.survey_name='sloan'
        self.survey=sloan_ukidss
        self.anything_odd='sloan-6'

class GZ4_ukidss(GZ4_base):
    def __init__(self,debug=False):
        self.debug=debug
        self.survey_name='ukidss'
        self.survey=sloan_ukidss
        self.anything_odd='ukidss-6'

class GZ4_ferengi(GZ4_base):
    def __init__(self,debug=False):
        self.debug=debug
        self.survey_name='ferengi'
        self.survey=ferengi
        self.anything_odd='ferengi-17'

class GZ4_candels(GZ4_base):
    def __init__(self,debug=False):
        self.debug=debug
        self.survey_name='candels'
        self.survey=candels
        self.anything_odd='candels-16'
            
