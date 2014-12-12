from sqlalchemy.sql import func
import re

#======================================================
#auto generate table classes from the existing database
class Tables:
    def __init__(self):
        pass

def class_factory(db,t,bk):
    class NewClass(db.Model):
        __bind_key__=bk
        __table__=db.Model.metadata.tables[t]
    NewClass.__name__=str(t)+'_'+bk
    return NewClass    
    
def get_tables(db,bk):
    MyTables=Tables()
    for t in db.Model.metadata.tables.keys():
        try:
            setattr(MyTables,str(t),class_factory(db,t,bk))
        except:
            pass
    return MyTables

#======================================================
#The base class for the two databases.
class Connect:
    def __init__(self,BC,session):
        self.BC=BC
        self.session = session
        self.vp={}
    def call_proc(self,proc,args=(),fetch=False):
        cursor=self.engine.raw_connection().cursor()
        result=cursor.callproc(proc,args=args)
        if fetch:
            result=cursor.stored_results().next().fetchall()
        cursor.close()
        return result
    def valid_path(self,p):
        l=len(p)
        p2=p+[-1]
        valid=True
        for i in range(l):
            valid = (valid) and (p2[i+1] in self.vp[p2[i]])
            if not valid:
                return valid
        return valid
    def get_answers(self):
        pass
    def get_nearest_obj(self):
        pass
    def get_obj_by_id(self):
        pass
    def get_rand_obj(self):
        pass
    def get_vote_path(self):
        pass
    def get_nodes(self):
        answers=self.get_answers()
        # order: answer, question, answer_id, group_id
        node_names=['name', 'question', 'answer_id']
        self.nodes=[dict(zip(node_names,i)+[('group',j)]) for i,j in zip(answers,self.group_id)]
         # check to make sure no node id was skipped
        # this makes sure the answer_id used in links matches up with the order of the nodes
        if len(self.nodes)<=self.nodes[-1]['answer_id']:
            # add a blank node there
            blank_node={'answer':'', 'question':'', 'answer_id':-1, 'group':-1}
            ct=0
            idx_to_append=[]
            for c,n in zip(self.nodes[:-1],self.nodes[1:]):
                dif=n['answer_id']-c['answer_id']
                if dif>1:
                    idx_to_append+=range(ct+1,ct+dif)
                ct+=dif
            for idx in idx_to_append:
                blank_node['answer_id']=idx
                self.nodes.insert(idx,blank_node)
    def get_links(self,path):
        path_dict={}
        odd_dict={}
        for p in path:
            i=map(int,p[0].split(','))
            # detect index answering the frist question in a classification
            # this will avoid the issue when people hit the reset button
            idx_first=[x for x,y in enumerate(i) if (y==1 or y==2 or y==3)]
            # only take the final time through the tree
            if len(idx_first)>0: # sometimes the first node is missing!
                i=i[idx_first[-1]:]
                i=[0]+i
                # check that all votes makes a vlid path through the tree (no missing or repeated nodes!)
                if self.valid_path(i):
                    if 14 in i:
                        odd_dict[i[-1]]=odd_dict.get(i[-1],0)+1
                        i=i[:-2]
                    elif 15 in i:
                        i=i[:-1]
                    for key in zip(i[:-1],i[1:]):
                        path_dict[key]=path_dict.get(key,0)+1
        self.odd_list=[]
        for key,value in odd_dict.iteritems():
            self.odd_list.append([key,value])
        self.odd_list.sort(key=lambda x: x[1])
        self.odd_list=self.odd_list[::-1]
        self.odd_list=[{'name':k[0], 'value':k[1]} for k in self.odd_list]
        self.links=[{'source':k[0], 'target':k[1], 'value': v} for k,v in path_dict.iteritems()]
    def run(self,argv='180 0'):
        if argv=='random':
            gal_name,gal_id,ra_gal,dec_gal,url=self.get_rand_obj()
        else:
            argv=re.findall(r"[\w.-]+",argv)
            L=len(argv)
            if L==1:
                gal_name,gal_id,ra_gal,dec_gal,url=self.get_obj_by_id(argv[0])
            else:
                ra,dec=map(float,argv)
                gal_name,gal_id,ra_gal,dec_gal,url=self.get_nearest_obj(ra,dec)
        path=self.get_vote_path(gal_id)
        self.get_links(path)
        # put it all together
        return {'nodes':self.nodes,'links':self.links,'image_url':url,'ra':ra_gal,'dec':dec_gal,'gal_name':gal_name,'odd_list':self.odd_list}
    
class GZ2(Connect):
    def __init__(self,db,app,BC):
        self.bind=db.get_engine(app,'gz2')
        Connect.__init__(self,BC,db.sessionmaker(bind=self.bind)())
        self.group_id=[0,1,2,4,2,3,3,3,3,3,3,3,3,3,5,5,1,1,1,5,5,5,5,5,5,2,2,2,3,3,3,3,3,3,3,3,3,5]
        self.vp=gz2_valid_path
        self.get_nodes()
    def get_answers(self):
        answers=self.BC.answers
        tasks=self.BC.tasks
        self.session.bind=self.bind
        result=self.session.query(answers.value,tasks.name,answers.id).\
                    join(tasks, answers.task_id==tasks.id).\
                    order_by(answers.id.asc()).all()
        return [['All','',0]]+map(list,result)
    def get_nearest_obj(self,ra_in,dec_in):
        a=self.BC.assets
        #this distance is correct up to multiplications factors (order is correct)
        dis=func.asin(func.sqrt(func.power(func.sin(0.5*func.radians(dec_in-a.dec)),2) + func.cos(func.radians(dec_in))*func.cos(func.radians(a.dec))*func.power(func.sin(.5*func.radians(ra_in-a.ra)),2)))
        result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).order_by(dis.asc()).first()
        return result
    def get_obj_by_id(self,name_in):
        a=self.BC.assets
        result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).filter(a.name==name_in).order_by(a.classification_count.desc()).first()
        return result
    def get_rand_obj(self):
        a=self.BC.assets
        result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).order_by(func.rand()).first()
        return result
    def get_vote_path(self,gal_id):
        a=self.BC.annotations
        ac=self.BC.asset_classifications
        c=self.BC.classifications
        result=self.session.query(func.group_concat(a.answer_id.op('ORDER BY')(a.id.asc())),ac.classification_id,c.user_id).\
               join(ac, a.classification_id==ac.classification_id).\
               join(c, c.id==ac.classification_id).\
               filter(ac.asset_id==gal_id).\
               filter(a.answer_id!=None).\
               group_by(ac.classification_id).all()
        return result

class GZ3(Connect):
    def __init__(self,db,app,BC):
        self.bind=db.get_engine(app,'gz3')
        Connect.__init__(self,BC,db.sessionmaker(bind=self.bind)())
        self.group_id=[0,1,2,5,2,3,3,3,3,3,3,3,3,3,6,6,1,1,1,6,6,6,6,6,6,2,2,2,3,3,3,3,3,3,3,3,3,6,4,2,
                       4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4]
        self.vp=gz3_valid_path
        self.get_nodes()
    def get_answers(self):
        a1=self.BC.answer_translations
        t=self.BC.task_translations
        a2=self.BC.answers
        result=self.session.query(a1.value,t.name,a1.answer_id).\
                    join(a2, a2.id==a1.answer_id).\
                    join(t, t.task_id==a2.task_id).\
                    filter(a1.locale=='en').\
                    filter(t.locale=='en').\
                    order_by(a1.answer_id.asc()).all()
        return [['All','',0]]+map(list,result)
    def get_nearest_obj(self,ra_in,dec_in):
        a=self.BC.assets
        #this distance is correct up to multiplications factors (order is correct)
        dis=func.asin(func.sqrt(func.power(func.sin(0.5*func.radians(dec_in-a.dec)),2) + func.cos(func.radians(dec_in))*func.cos(func.radians(a.dec))*func.power(func.sin(.5*func.radians(ra_in-a.ra)),2)))
        result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).order_by(dis.asc()).first()
        return result
    def get_obj_by_id(self,name_in):
        a=self.BC.assets
        result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).filter(a.name==name_in).order_by(a.classification_count.desc()).first()
        return result
    def get_rand_obj(self):
        a=self.BC.assets
        result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).order_by(func.rand()).first()
        return result
    def get_vote_path(self,gal_id):
        a=self.BC.annotations
        ac=self.BC.asset_classifications
        c=self.BC.classifications
        result=self.session.query(func.group_concat(a.answer_id.op('ORDER BY')(a.id.asc())),ac.classification_id,c.zooniverse_user_id).\
               join(ac, a.classification_id==ac.classification_id).\
               join(c, c.id==ac.classification_id).\
               filter(ac.asset_id==gal_id).\
               filter(a.answer_id!=None).\
               group_by(ac.classification_id).all()
        return result

#======================================================

gz2_valid_path={0:[1,2,3],
                1:[16,17,18],
                2:[4,5],
                3:[-1],
                4:[25,26,27],
                5:[6,7],
                6:[8,9],
                7:[8,9],
                8:[28,29,30],
                9:[10,11,12,13],
                10:[14,15],
                11:[14,15],
                12:[14,15],
                13:[14,15],
                14:[19,20,21,22,23,24,38],
                15:[-1],
                16:[14,15],
                17:[14,15],
                18:[14,15],
                19:[-1],
                20:[-1],
                21:[-1],
                22:[-1],
                23:[-1],
                24:[-1],
                25:[14,15],
                26:[14,15],
                27:[14,15],
                28:[31,32,33,34,36,37],
                29:[31,32,33,34,36,37],
                30:[31,32,33,34,36,37],
                31:[10,11,12,13],
                32:[10,11,12,13],
                33:[10,11,12,13],
                34:[10,11,12,13],
                36:[10,11,12,13],
                37:[10,11,12,13],
                38:[-1]}

gz3_valid_path={0:[1,2,3],
                1:[16,17,18],
                2:[39,40],
                3:[-1],
                4:[25,26,27],
                5:[6,7],
                6:[8,9,28,29,30],
                7:[8,9,28,29,30],
                8:[28,29,30],
                9:[10,11,12,13],
                10:[14,15],
                11:[14,15],
                12:[14,15],
                13:[14,15],
                14:[19,20,21,22,23,24,38],
                15:[-1],
                16:[14,15],
                17:[14,15],
                18:[14,15],
                19:[-1],
                20:[-1],
                21:[-1],
                22:[-1],
                23:[-1],
                24:[-1],
                25:[14,15],
                26:[14,15],
                27:[14,15],
                28:[31,32,33,34,36,37],
                29:[31,32,33,34,36,37],
                30:[31,32,33,34,36,37],
                31:[10,11,12,13],
                32:[10,11,12,13],
                33:[10,11,12,13],
                34:[10,11,12,13],
                36:[10,11,12,13],
                37:[10,11,12,13],
                38:[-1],
                39:[60,50,51,52,53,54],
                40:[4,5],
                41:[],
                42:[],
                43:[45,46],
                44:[55,56],
                45:[55,56],
                46:[55,56],
                47:[43,44],
                48:[43,44],
                49:[43,44],
                50:[43,44],
                51:[47,48,49,59],
                52:[47,48,49,59],
                53:[47,48,49,59],
                54:[47,48,49,59],
                55:[57,58],
                56:[57,58],
                57:[14,15],
                58:[14,15],
                59:[6,7],
                60:[16,17,18,55,56]}
