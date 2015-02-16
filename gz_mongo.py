import re
from random import random
import gz2
import gz3
import gz4_sloan_ukidss as sloan_ukidss
import gz4_ferengi as ferengi
import gz4_candels as candels

#=====================================================
#function to split lists on a value, used to pull out
#anything odd nodes
#taken from http://stackoverflow.com/questions/4322705/split-a-list-into-nested-lists-on-a-value
def ssplit2(seq,splitters):
    seq=list(seq)
    if splitters and seq:
        splitters=set(splitters).intersection(seq)
        if splitters:
            result=[]
            begin=0
            for end in range(len(seq)):
                if seq[end] in splitters:
                    if end > begin:
                        result.append(seq[begin:end])
                    begin=end+1
            if begin<len(seq):
                result.append(seq[begin:])
            return result
    return [seq]

#=====================================================

class GZ_base:
    def __init__(self):
        self.survey_name=''
        self.survey=None
        self.connect=None
        self.debug=False
        self.anything_odd=''
        self.get_links=self.get_links_mongo
    def get_links_mongo(self,m_id):
        #m_id is the mongo "_id" value for the galaxy subject
        #find all classifications with the propper subject id
        c=self.connect.db.galaxy_zoo_classifications.find({'subject_ids':m_id})
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
    def get_links_sql(self,m_id):
        # The annotations field is different for the SQL converted subjects
        c=self.connect.db.galaxy_zoo_classifications.find({'subject_ids':m_id})
        path_dict={}
        odd_dict={}
        for j in c:
            i=j['annotations']
            # detect index answering the frist question in a classification
            # this will avoid the issue when people hit the reset button
            idx_first=[x for x,y in enumerate(i) if (y==1 or y==2 or y==3)]
            # only take the final time through the tree
            if len(idx_first)>0: # sometimes the first node is missing!
                i=i[idx_first[-1]:]
                i=[0]+i
                # check that all votes makes a vlid path through the tree (no missing or repeated nodes!)
                if self.survey.valid_path(i):
                    if 14 in i:
                        #could be more then 1 anything odd answer
                        ii,jj=ssplit2(i,[14])
                        for j in jj:
                            odd_dict[j]=odd_dict.get(j,0)+1
                        i=ii
                    elif 15 in i:
                        i=i[:-1]
                    for key in zip(i[:-1],i[1:]):
                        path_dict[key]=path_dict.get(key,0)+1
        self.odd_list=map(list,odd_dict.items())
        self.odd_list.sort(key=lambda x: x[1])
        self.odd_list=self.odd_list[::-1]
        self.odd_list=[{'name':k[0], 'value':k[1]} for k in self.odd_list]
        self.links=[{'source':k[0], 'target':k[1], 'value': v} for k,v in path_dict.iteritems()]
    def run(self,argv='180 0'):
        if argv=='random':
            s=self.connect.db.galaxy_zoo_subjects.find_one({'metadata.survey':self.survey_name, 'random':{'$gt':random()}})
        else:
            argv=re.findall(r"[\w.-]+",argv)
            L=len(argv)
            if L==1:
                s=self.connect.db.galaxy_zoo_subjects.find_one({'zooniverse_id':argv[0]})
            else:
                ra,dec=map(float,argv)
                s=self.connect.db.galaxy_zoo_subjects.find_one({'location_geo':{'$near':{'$geometry':{ 'type' : 'Point' , 'coordinates' :[ra-180,dec]}}}, 'metadata.survey':self.survey_name})
        if self.debug:
            pprint(s)
        self.get_links(s['_id'])
        return {'nodes':self.survey.nodes,'links':self.links,'image_url':s['location']['standard'],'ra':s['coords'][0],'dec':s['coords'][1],'gal_name':s['zooniverse_id'],'odd_list':self.odd_list}

class GZ2(GZ_base):
    def __init__(self,connect,debug=False):
        self.connect=connect
        self.debug=debug
        self.survey_name='GZ2'
        self.survey=gz2
        self.anything_odd=None
        self.get_links=self.get_links_sql

class GZ3(GZ_base):
    def __init__(self,connect,debug=False):
        self.connect=connect
        self.debug=debug
        self.survey_name='Hubble'
        self.survey=gz3
        self.anything_odd=None
        self.get_links=self.get_links_sql
        
class GZ4_sloan(GZ_base):
    def __init__(self,connect,debug=False):
        self.connect=connect
        self.debug=debug
        self.survey_name='sloan'
        self.survey=sloan_ukidss
        self.anything_odd='sloan-6'
        self.get_links=self.get_links_mongo

class GZ4_ukidss(GZ_base):
    def __init__(self,connect,debug=False):
        self.connect=connect
        self.debug=debug
        self.survey_name='ukidss'
        self.survey=sloan_ukidss
        self.anything_odd='ukidss-6'
        self.get_links=self.get_links_mongo

class GZ4_ferengi(GZ_base):
    def __init__(self,connect,debug=False):
        self.connect=connect
        self.debug=debug
        self.survey_name='ferengi'
        self.survey=ferengi
        self.anything_odd='ferengi-17'
        self.get_links=self.get_links_mongo

class GZ4_candels(GZ_base):
    def __init__(self,connect,debug=False):
        self.connect=connect
        self.debug=debug
        self.survey_name='candels'
        self.survey=candels
        self.anything_odd='candels-16'
        self.get_links=self.get_links_mongo
            
