from pymongo import MongoClient
from gz_mongo import *
from scipy import *
import progressbar as pb

class connect():
    def __init__(self,db):
        self.db=db

def dict_dejson(data):
    newdict={}
    for k,v in [(key,d[key]) for d in data for key in d]:
        if k not in newdict:
            newdict[k]=[v]
        else:
            newdict[k].append(v)
    newdict={k:array(v) for k,v in newdict.iteritems()}
    return newdict

def weight_pass(sub,sql_db,num_resp, Gz, p, pbar, fr_weight=False):
    pbar.start()
    for sdx,s in enumerate(sub):
        if p==1:
            Gz.get_links_sql(s['_id'],weight=False)
        else:
            Gz.get_links_sql(s['_id'],weight=True)
        links=dict_dejson(Gz.links)
        total_votes=links['value'][links['source']==0].sum()
        K={}
        for q in unique(links['source']):
            idx=(links['source']==q)
            t=links['target'][idx]
            v=links['value'][idx]
            fr=v/float(v.sum())
            k=1+(2./num_resp[q])*(fr-1)
            if fr_weight:
                k*=v/total_votes
            K.update(zip(t,k))
        #anything odd votes
        odd_list=dict_dejson(Gz.odd_list)
        num_star=links['value'][links['target']==3]
        num_odd=total_votes-num_star
        K[14]=odd_list['value'].sum()/float(num_odd)
        K[15]=1-K[14]
        fr_odd=odd_list['value']/float(odd_list['value'].sum())
        k=1+(2./num_resp[14])*(fr_odd-1)
        if fr_weight:
            K[14]*=odd_list['value'].sum()/total_votes
            K[15]*=(num_odd-odd_list['value'].sum())/total_votes
            k*=odd_list['value']/total_votes
        K.update(zip(odd_list['name'],k))
        for i,v in Gz.user_id_sql.iteritems():
            ki=array([K[j] for j in v[1:]])
            u=sql_db.find_one({'user_id_sql':i})
            if u is None:
                u={'user_id_sql': i}
            if 'pass_%i'%p not in u:
                u['pass_%i'%p]={
                    'k_mean': ki.mean(),
                    'k_tot': len(ki),
                    'gal_tot': 1
                    }
            else:
                new_tot=u['pass_%i'%p]['k_tot']+len(ki)
                new_sum=u['pass_%i'%p]['k_mean']*u['pass_1']['k_tot']+ki.sum()
                u['pass_%i'%p]['k_mean']=new_sum/new_tot
                u['pass_%i'%p]['ktot']=new_tot
                u['pass_%i'%p]['gal_tot']+=1
            u['k_mean']=u['pass_%i'%p]['k_mean']
            sql_db.update({'user_id_sql':i}, {'$set':u}, upsert=True)
        pbar.update(sdx)
    pbar.finish()

client=MongoClient('localhost',27017)      
con=connect(client['galaxy_zoo'])
Gz2=GZ2(con)
Gz3=GZ3(con)

gz2_num_resp={k:len(v) for k,v in gz2.vp.iteritems()}
gz3_num_resp={k:len(v) for k,v in gz3.vp.iteritems()}
    
for p in [1,2,3]:
    gz2_sub=con.db.galaxy_zoo_subjects.find({'metadata.survey':'GZ2'})
    widgets = ['GZ2 Pass %i: '%p, pb.Percentage(), ' ', pb.Bar(marker='0',left='[',right=']'),' ', pb.ETA()]
    pbar = pb.ProgressBar(widgets=widgets, maxval=sub.count())
    weight_pass(gz2_sub,con.db.gz2_sql_users,gz2_num_resp,Gz2,p,pbar)

for p in [1,2,3]:
    gz3_sub=con.db.galaxy_zoo_subjects.find({'metadata.survey':'Hubble'})
    widgets = ['GZ3 Pass %i: '%p, pb.Percentage(), ' ', pb.Bar(marker='0',left='[',right=']'),' ', pb.ETA()]
    pbar = pb.ProgressBar(widgets=widgets, maxval=sub.count())
    weight_pass(gz3_sub,con.db.gz3_sql_users,gz3_num_resp,Gz3,p,pbar)
