from sqlalchemy.sql import func, between
from random import randint
import re
import math
import warnings
warnings.simplefilter("ignore")

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

#======================================================
#function to calculate the bounding box for an (RA,DEC) search
def geo_bounding_box(ra,dec,size=1):
    #default to a 1-deg box
    #all in units of deg
    ra=math.radians(ra)
    dec=math.radians(dec)
    size=math.radians(size)
    min_dec=dec-size
    max_dec=dec+size
    if (min_dec > -math.pi/2) and (max_dec < math.pi/2):
        delta_ra = math.asin(math.sin(size)/math.cos(dec))
        min_ra=ra-delta_ra
        if min_ra < 0:
            min_ra+=2*math.pi
        max_ra=ra+delta_ra
        if max_ra > 2*math.pi:
            max_ra-=2*math.pi
    else:
        min_dec=max(min_dec,-math.pi/2)
        max_dec=min(max_dec,math.pi/2)
        min_ra=0
        max_ra=2*math.pi
    if min_ra>max_ra:
        return [[(math.degrees(min_ra),360),(0,math.degrees(max_ra))],(math.degrees(min_dec),math.degrees(max_dec))]
    return [(math.degrees(min_ra),math.degrees(max_ra)),(math.degrees(min_dec),math.degrees(max_dec))]

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
        # This funciton is not needed since this is not hard coded below
        # This hard coding reduces server load and page load time
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
        #self.group_id=[0,1,2,4,2,3,3,3,3,3,3,3,3,3,5,5,1,1,1,5,5,5,5,5,5,2,2,2,3,3,3,3,3,3,3,3,3,5]
        self.vp=gz2_valid_path
        self.nodes=gz2_nodes
    def get_answers(self):
        answers=self.BC.answers
        tasks=self.BC.tasks
        self.session.bind=self.bind
        result=self.session.query(answers.value,tasks.name,answers.id).\
                    join(tasks, answers.task_id==tasks.id).\
                    order_by(answers.id.asc()).all()
        return [['All','',0]]+map(list,result)
    def get_nearest_obj(self,ra_in,dec_in,size=2):
        a=self.BC.assets
        #find a bounding box to speed up search (size depended on search regon)
        if (ra_in<60) or (ra_in>308.5):
            if (dec_in+size)<-1:
                size=abs(dec_in+1)
            elif (dec_in-size)>1:
                size=abs(dec_in-1)
        else:
            if (dec_in+size)<-3:
                size=abs(dec_in+3)
            elif (dec_in-size)>76:
                size=abs(dec_in-76)
        box=geo_bounding_box(ra_in,dec_in,size=size)
        #this distance is correct up to multiplications factors (order is correct)
        dis=func.asin(func.sqrt(func.power(func.sin(0.5*func.radians(dec_in-a.dec)),2) + func.cos(func.radians(dec_in))*func.cos(func.radians(a.dec))*func.power(func.sin(.5*func.radians(ra_in-a.ra)),2)))
        if isinstance(box[0],list):
            #the search wraps around 360
           result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).filter(between(a.dec,box[1][0],box[1][1])).filter((between(a.ra,box[0][0][0],box[0][0][1]))|(between(a.ra,box[0][1][0],box[0][1][1]))).order_by(dis.asc()).first()
        else:
            result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).filter(between(a.ra,box[0][0],box[0][1])).filter(between(a.dec,box[1][0],box[1][1])).order_by(dis.asc()).first()
        #result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).order_by(dis.asc()).first()
        if result is None:
            result=self.get_nearest_obj(ra_in,dec_in,size=size+20)
        return result
    def get_obj_by_id(self,name_in):
        a=self.BC.assets
        result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).filter(a.name==name_in).order_by(a.classification_count.desc()).first()
        return result
    def get_rand_obj(self):
        a=self.BC.assets
        #there are 355,990 assets in GZ2, no gaps in the id number (makes life easy)
        rand_id=randint(1,355990)
        result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).filter(a.id==rand_id).first()
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
        #self.group_id=[0,1,2,5,2,3,3,3,3,3,3,3,3,3,6,6,1,1,1,6,6,6,6,6,6,2,2,2,3,3,3,3,3,3,3,3,3,6,4,2,
        #              4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4]
        self.vp=gz3_valid_path
        self.nodes=gz3_nodes
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
    def get_nearest_obj(self,ra_in,dec_in,size=5):
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
        #there are 169,944 assets in GZ3, no gaps in the id number (makes life easy)
        rand_id=randint(1,169944)
        result=self.session.query(a.name,a.id,a.ra,a.dec,a.location).filter(a.id==rand_id).first()
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
                19:[-1,20,21,22,23,24,38],
                20:[-1,19,21,22,23,24,38],
                21:[-1,19,20,22,23,24,38],
                22:[-1,19,20,21,23,24,38],
                23:[-1,19,20,21,22,24,38],
                24:[-1,19,20,21,22,23,38],
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
                38:[-1,19,20,21,22,23,24]}

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
                19:[-1,20,21,22,23,24,38],
                20:[-1,19,21,22,23,24,38],
                21:[-1,19,20,22,23,24,38],
                22:[-1,19,20,21,23,24,38],
                23:[-1,19,20,21,22,24,38],
                24:[-1,19,20,21,22,23,38],
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
                38:[-1,19,20,21,22,23,24],
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

#hardcode the nodes list so fewer sql calls are made to the server
gz2_nodes=[
    {"group": 0, "question": "", "name": "All", "answer_id": 0},
    {"group": 1, "question": "Is the galaxy simply smooth and rounded, with no sign of a disk?", "name": "Smooth", "answer_id": 1},
    {"group": 2, "question": "Is the galaxy simply smooth and rounded, with no sign of a disk?", "name": "Features or disk", "answer_id": 2},
    {"group": 4, "question": "Is the galaxy simply smooth and rounded, with no sign of a disk?", "name": "Star or artifact", "answer_id": 3},
    {"group": 2, "question": "Could this be a disk viewed edge-on?", "name": "Yes", "answer_id": 4},
    {"group": 3, "question": "Could this be a disk viewed edge-on?", "name": "No", "answer_id": 5},
    {"group": 3, "question": "Is there a sign of a bar feature through the centre of the galaxy?", "name": "Bar", "answer_id": 6},
    {"group": 3, "question": "Is there a sign of a bar feature through the centre of the galaxy?", "name": "No bar", "answer_id": 7},
    {"group": 3, "question": "Is there any sign of a spiral arm pattern?", "name": "Spiral", "answer_id": 8},
    {"group": 3, "question": "Is there any sign of a spiral arm pattern?", "name": "No spiral", "answer_id": 9},
    {"group": 3, "question": "How prominent is the central bulge, compared with the rest of the galaxy?", "name": "No bulge", "answer_id": 10},
    {"group": 3, "question": "How prominent is the central bulge, compared with the rest of the galaxy?", "name": "Just noticeable", "answer_id": 11},
    {"group": 3, "question": "How prominent is the central bulge, compared with the rest of the galaxy?", "name": "Obvious", "answer_id": 12},
    {"group": 3, "question": "How prominent is the central bulge, compared with the rest of the galaxy?", "name": "Dominant", "answer_id": 13},
    {"group": 5, "question": "Is there anything odd?", "name": "Yes", "answer_id": 14},
    {"group": 5, "question": "Is there anything odd?", "name": "No", "answer_id": 15},
    {"group": 1, "question": "How rounded is it?", "name": "Completely round", "answer_id": 16},
    {"group": 1, "question": "How rounded is it?", "name": "In between", "answer_id": 17},
    {"group": 1, "question": "How rounded is it?", "name": "Cigar shaped", "answer_id": 18},
    {"group": 5, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Ring", "answer_id": 19},
    {"group": 5, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Lens or arc", "answer_id": 20},
    {"group": 5, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Disturbed", "answer_id": 21},
    {"group": 5, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Irregular", "answer_id": 22},
    {"group": 5, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Other", "answer_id": 23},
    {"group": 5, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Merger", "answer_id": 24},
    {"group": 2, "question": "Does the galaxy have a bulge at its centre? If so, what shape?", "name": "Rounded", "answer_id": 25},
    {"group": 2, "question": "Does the galaxy have a bulge at its centre? If so, what shape?", "name": "Boxy", "answer_id": 26},
    {"group": 2, "question": "Does the galaxy have a bulge at its centre? If so, what shape?", "name": "No bulge", "answer_id": 27},
    {"group": 3, "question": "How tightly wound do the spiral arms appear?", "name": "Tight", "answer_id": 28},
    {"group": 3, "question": "How tightly wound do the spiral arms appear?", "name": "Medium", "answer_id": 29},
    {"group": 3, "question": "How tightly wound do the spiral arms appear?", "name": "Loose", "answer_id": 30},
    {"group": 3, "question": "How many spiral arms are there?", "name": "1", "answer_id": 31},
    {"group": 3, "question": "How many spiral arms are there?", "name": "2", "answer_id": 32},
    {"group": 3, "question": "How many spiral arms are there?", "name": "3", "answer_id": 33},
    {"group": 3, "question": "How many spiral arms are there?", "name": "4", "answer_id": 34},
    {"answer": "", "group": -1, "question": "", "answer_id": 35},
    {"group": 3, "question": "How many spiral arms are there?", "name": "More than 4", "answer_id": 36},
    {"group": 3, "question": "How many spiral arms are there?", "name": "Can't tell", "answer_id": 37},
    {"group": 5, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Dust lane", "answer_id": 38}]

gz3_nodes=[
    {"group": 0, "question": "", "name": "All", "answer_id": 0},
    {"group": 1, "question": "Is the galaxy simply smooth and rounded, with no sign of a disk?", "name": "Smooth", "answer_id": 1},
    {"group": 2, "question": "Is the galaxy simply smooth and rounded, with no sign of a disk?", "name": "Features or disk", "answer_id": 2},
    {"group": 5, "question": "Is the galaxy simply smooth and rounded, with no sign of a disk?", "name": "Star or artifact", "answer_id": 3},
    {"group": 2, "question": "Could this be a disk viewed edge-on?", "name": "Yes", "answer_id": 4},
    {"group": 3, "question": "Could this be a disk viewed edge-on?", "name": "No", "answer_id": 5},
    {"group": 3, "question": "Is there a sign of a bar feature through the centre of the galaxy?", "name": "Bar", "answer_id": 6},
    {"group": 3, "question": "Is there a sign of a bar feature through the centre of the galaxy?", "name": "No bar", "answer_id": 7},
    {"group": 3, "question": "Is there any sign of a spiral arm pattern?", "name": "Spiral", "answer_id": 8},
    {"group": 3, "question": "Is there any sign of a spiral arm pattern?", "name": "No spiral", "answer_id": 9},
    {"group": 3, "question": "How prominent is the central bulge, compared with the rest of the galaxy?", "name": "No bulge", "answer_id": 10},
    {"group": 3, "question": "How prominent is the central bulge, compared with the rest of the galaxy?", "name": "Just noticeable", "answer_id": 11},
    {"group": 3, "question": "How prominent is the central bulge, compared with the rest of the galaxy?", "name": "Obvious", "answer_id": 12},
    {"group": 3, "question": "How prominent is the central bulge, compared with the rest of the galaxy?", "name": "Dominant", "answer_id": 13},
    {"group": 6, "question": "Is there anything odd?", "name": "Yes", "answer_id": 14},
    {"group": 6, "question": "Is there anything odd?", "name": "No", "answer_id": 15},
    {"group": 1, "question": "How rounded is it?", "name": "Completely round", "answer_id": 16},
    {"group": 1, "question": "How rounded is it?", "name": "In between", "answer_id": 17},
    {"group": 1, "question": "How rounded is it?", "name": "Cigar shaped", "answer_id": 18},
    {"group": 6, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Ring", "answer_id": 19},
    {"group": 6, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Lens or arc", "answer_id": 20},
    {"group": 6, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Disturbed", "answer_id": 21},
    {"group": 6, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Irregular", "answer_id": 22},
    {"group": 6, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Other", "answer_id": 23},
    {"group": 6, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Merger", "answer_id": 24},
    {"group": 2, "question": "Does the galaxy have a bulge at its centre? If so, what shape?", "name": "Rounded", "answer_id": 25},
    {"group": 2, "question": "Does the galaxy have a bulge at its centre? If so, what shape?", "name": "Boxy", "answer_id": 26},
    {"group": 2, "question": "Does the galaxy have a bulge at its centre? If so, what shape?", "name": "No bulge", "answer_id": 27},
    {"group": 3, "question": "How tightly wound do the spiral arms appear?", "name": "Tight", "answer_id": 28},
    {"group": 3, "question": "How tightly wound do the spiral arms appear?", "name": "Medium", "answer_id": 29},
    {"group": 3, "question": "How tightly wound do the spiral arms appear?", "name": "Loose", "answer_id": 30},
    {"group": 3, "question": "How many spiral arms are there?", "name": "1", "answer_id": 31},
    {"group": 3, "question": "How many spiral arms are there?", "name": "2", "answer_id": 32},
    {"group": 3, "question": "How many spiral arms are there?", "name": "3", "answer_id": 33},
    {"group": 3, "question": "How many spiral arms are there?", "name": "4", "answer_id": 34},
    {"answer": "", "group": -1, "question": "", "answer_id": 35},
    {"group": 3, "question": "How many spiral arms are there?", "name": "More than 4", "answer_id": 36},
    {"group": 3, "question": "How many spiral arms are there?", "name": "Can't tell", "answer_id": 37},
    {"group": 6, "question": "Is the odd feature a ring, or is the galaxy disturbed or irregular?", "name": "Dust lane", "answer_id": 38},
    {"group": 4, "question": "Does the galaxy have a mostly clumpy appearance?", "name": "Yes", "answer_id": 39},
    {"group": 2, "question": "Does the galaxy have a mostly clumpy appearance?", "name": "No", "answer_id": 40},
    {"group": 4, "question": "Are there multiple clumps?", "name": "Yes", "answer_id": 41},
    {"group": 4, "question": "Are there multiple clumps?", "name": "No", "answer_id": 42},
    {"group": 4, "question": "Is there one clump which is clearly brighter than the others?", "name": "Yes", "answer_id": 43},
    {"group": 4, "question": "Is there one clump which is clearly brighter than the others?", "name": "No", "answer_id": 44},
    {"group": 4, "question": "Is the brightest clump central to the galaxy?", "name": "Yes", "answer_id": 45},
    {"group": 4, "question": "Is the brightest clump central to the galaxy?", "name": "No", "answer_id": 46},
    {"group": 4, "question": "Do the clumps appear in a straight line, a chain, or a cluster?", "name": "Straight Line", "answer_id": 47},
    {"group": 4, "question": "Do the clumps appear in a straight line, a chain, or a cluster?", "name": "Chain", "answer_id": 48},
    {"group": 4, "question": "Do the clumps appear in a straight line, a chain, or a cluster?", "name": "Cluster", "answer_id": 49},
    {"group": 4, "question": "How many clumps are there?", "name": "2", "answer_id": 50},
    {"group": 4, "question": "How many clumps are there?", "name": "3", "answer_id": 51},
    {"group": 4, "question": "How many clumps are there?", "name": "4", "answer_id": 52},
    {"group": 4, "question": "How many clumps are there?", "name": "More than 4", "answer_id": 53},
    {"group": 4, "question": "How many clumps are there?", "name": "Can't tell", "answer_id": 54},
    {"group": 4, "question": "Does the galaxy appear symmetrical?", "name": "Yes", "answer_id": 55},
    {"group": 4, "question": "Does the galaxy appear symmetrical?", "name": "No", "answer_id": 56},
    {"group": 4, "question": "Do the clumps appear to be embedded within a larger object?", "name": "Yes", "answer_id": 57},
    {"group": 4, "question": "Do the clumps appear to be embedded within a larger object?", "name": "No", "answer_id": 58},
    {"group": 4, "question": "Do the clumps appear in a straight line, a chain, or a cluster?", "name": "Spiral", "answer_id": 59},
    {"group": 4, "question": "How many clumps are there?", "name": "1", "answer_id": 60}]
