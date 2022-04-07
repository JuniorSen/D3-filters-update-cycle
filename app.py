from email import message
from os import stat
from attr import dataclass
from flask import Flask,render_template,request,session,jsonify
import csv
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from scipy.interpolate import make_interp_spline
import pickle
from os.path import exists
from helperFuncs import co_association_matrix
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import DBSCAN
from sklearn.cluster import OPTICS
from sklearn.cluster import MeanShift
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import Birch
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import SpectralClustering
from sklearn.mixture import GaussianMixture
import sys

app = Flask(__name__) #create app instance
app.secret_key = 'example' #store this in an environment variable for live apps.
surveyFilePath = 'input/surveyData/features_'
sigLocFilePath = 'input/SignificantLocations/features_'

fileFeatures = {
    surveyFilePath:['Survey PCA', 'Survey Performance'],
    sigLocFilePath:['Hometime', 'Significant Location'],
}
patientIds = ['U2201583859', 'U7744128165', 'U7331358608', 'U9119126792', 'U4172114993', 'U1954110644', 'U1606505063', 'U1771421483', 'U9938684473', 'U6321806987', 'U5501702863', 'U9864604466', 'U0328336314', 'U8514953341', 'U3826134542', 'U7851221787', 'U2287161257', 'U5342719148', 'U1128597896', 'U1456972679', 'U3600685320']

meta1 = {'panelId':'#panel1Viz','f':None,'f_opt':[],'pid':"U1606505063"}
meta2 = {'panelId':'#panel2Viz','f':None,'f_opt':[],'pid':"U7744128165"}

state = {1:0, 2:0}

#homepage
@app.route('/',methods=['GET','POST'])
def index():
    p1ID = request.form.get('p1ID')
    p1Features = []
    if(p1ID != None and p1ID != meta1['pid']):
        meta1['pid'] = p1ID
        meta1['f'] = None
        state[1] = 1
        state[2] = 0

    for fileloc in list(fileFeatures.keys()):
        if(exists(fileloc+meta1['pid']+'.csv')):
            p1Features.extend(fileFeatures[fileloc])
    f1 = request.form.get('f1')
    if(f1 != None and f1 != meta1['f']):
        meta1['f'] = f1
        state[1] = 1
        state[2] = 0
    if(meta1['f'] == None):
        meta1['f_opt'] = []
    elif(meta1['f'] == 'Survey PCA'):
        optList = request.form.getlist('svp1_opt')
        if (meta1['f_opt'] == []) and optList == [] or meta1['f_opt'][0] not in ['mood','anxiety','social','sleep','psychosis']:
            meta1['f_opt'] = ['mood']
        elif optList != []:
            meta1['f_opt'] = optList
            state[1] = 1
            state[2] = 0
    elif(meta1['f'] == 'Survey Performance'):
        optList = request.form.getlist('svPer1')
        if (meta1['f_opt'] == [] and optList == []) or meta1['f_opt'][0] not in ['Aggregate','Complete']:
            meta1['f_opt'] = ['Aggregate', "Natural"]
        if(optList and (optList[0] == 'Aggregate' or optList[0] == 'Complete')):
            meta1['f_opt'] = [optList[0]]
            state[1] = 1
            state[2] = 0
        if(optList and optList[1]):
            meta1['f_opt'].append(optList[1])
    elif(meta1['f'] == 'Hometime' or meta1['f'] == 'Significant Location'):
        my = request.form.get('p1MY')
        df = pd.read_csv(sigLocFilePath+meta1['pid']+'.csv')
        temp = pd.to_datetime(df['start'],dayfirst=True)
        validMonths = {}
        month = temp.min().month
        year = temp.min().year
        maxmonth = temp.max().month
        maxyear = temp.max().year
        minyear = temp.min().year
        while(year <= maxyear):
            yearlist = []
            if(year != maxyear):
                while(month <= 12): 
                    yearlist.append(month)
                    month += 1
                validMonths[year] = yearlist
                month = 1
            else:
                while(month <= maxmonth):
                    yearlist.append(month)
                    month += 1
                validMonths[year] = yearlist
            year += 1
        timeRange = (minyear, min(validMonths[minyear]), maxyear, max(validMonths[maxyear]))        
        if(my != None):
            state[2] = 0
            state[1] = 1  
            try:
                M, Y = map(int,my.split('-'))
                if(Y not in validMonths or M not in validMonths[Y]):
                    M = maxmonth
                    Y = maxyear
            except:
                M, Y = (timeRange[3], timeRange[2])    
        else:
            try:
                M, Y, _ = meta1['f_opt']
            except:
                M, Y = (timeRange[3], timeRange[2])
        meta1['f_opt'] = [M,Y,timeRange]

    
    p2ID = request.form.get('p2ID')
    p2Features = []
    if(p2ID != None and p2ID != meta2['pid']):
        meta2['pid'] = p2ID
        meta2['f'] = None
        state[1] = 0
        state[2] = 1
    for fileloc in list(fileFeatures.keys()):
        if(exists(fileloc+meta2['pid']+'.csv')):
            p2Features.extend(fileFeatures[fileloc])
    f2 = request.form.get('f2')
    if(f2 != None and f2 != meta2['f']):
        meta2['f'] = f2
        state[1] = 0
        state[2] = 1
    if(meta2['f'] == None):
        meta2['f_opt'] = []
    elif(meta2['f'] == 'Survey PCA'):
        optList = request.form.getlist('svp2_opt')
        if (meta2['f_opt'] == [] and optList == []) or meta2['f_opt'][0] not in ['mood','anxiety','social','sleep','psychosis']:
            meta2['f_opt'] = ['mood']
        elif optList != []:
            meta2['f_opt'] = optList
            state[1] = 0
            state[2] = 1
    elif(meta2['f'] == 'Survey Performance'):
        optList = request.form.getlist('svPer2')
        if (meta2['f_opt'] == [] and optList == []) or meta1['f_opt'][0] not in ['Aggregate','Complete']:
            meta2['f_opt'] = ['Aggregate', "Natural"]
        if(optList and (optList[0] == 'Aggregate' or optList[0] == 'Complete')):
            meta2['f_opt'] = [optList[0]]
            state[1] = 0
            state[2] = 1
        if(optList and optList[1]):
            meta2['f_opt'].append(optList[1])       
    elif(meta2['f'] == 'Hometime' or meta2['f'] == 'Significant Location'):
        my = request.form.get('p2MY')
        df = pd.read_csv(sigLocFilePath+meta2['pid']+'.csv')
        temp = pd.to_datetime(df['start'],dayfirst=True)
        validMonths = {}
        month = temp.min().month
        year = temp.min().year
        maxmonth = temp.max().month
        maxyear = temp.max().year
        minyear = temp.min().year
        while(year <= maxyear):
            yearlist = []
            if(year != maxyear):
                while(month <= 12): 
                    yearlist.append(month)
                    month += 1
                validMonths[year] = yearlist
                month = 1
            else:
                while(month <= maxmonth):
                    yearlist.append(month)
                    month += 1
                validMonths[year] = yearlist
            year += 1
        timeRange = (minyear, min(validMonths[minyear]), maxyear, max(validMonths[maxyear]))
        if(my != None):       
            state[2] = 1
            state[1] = 0     
            try:
                M, Y = map(int,my.split('-'))
                if(Y not in validMonths or M not in validMonths[Y]):
                    M = maxmonth
                    Y = maxyear
            except:
                M, Y = (timeRange[3], timeRange[2])
        else:
            try:
                M, Y, _ = meta2['f_opt']
            except:
                M, Y = (timeRange[3], timeRange[2])
        meta2['f_opt'] = [M,Y,timeRange]

    selected = {'p1ID':meta1['pid'], 'p2ID':meta2['pid'],
                'f1':meta1['f'], 'f2':meta2['f']}

    options = {'f1':p1Features, 'f2':p2Features, 
               'f1_opt':meta1['f_opt'], 'f2_opt':meta2['f_opt']}
    return render_template('base.html',selected=selected,options=options,patientIds=patientIds)

@app.route('/render')
def render():
    curState = []
    curState.append(state[1])
    curState.append(state[2])
    curState.append(meta1)
    curState.append(meta2)
    return jsonify(curState)

def sigLocExtract(meta):
    df = pd.read_csv(sigLocFilePath+meta['pid']+'.csv')
    M, Y, _ = tuple(meta['f_opt'])
    df = df.loc[(pd.DatetimeIndex(df.start).month == M) & (pd.DatetimeIndex(df.start).year == Y)]
    grouped = df.groupby('start')
    data = [meta]
    for name, group in grouped:
        dic = {}
        dic['ActivityDate'] = name.split(' ')[0]
        cols = ['latitude','longitude','proportion']
        locs = []
        for i in range(len(group)):
            locDet = {}
            for col in cols:
                locDet[col] = list(group[col])[i]
            locs.append(locDet)
        dic['locations'] = locs
        data.append(dic)
    return data

@app.route('/sigLocdata')
def sigLocdata():
    data1 = []
    data2 = []
    if(meta1['f'] == 'Hometime' or meta1['f'] == 'Significant Location'):
        data1 = sigLocExtract(meta1)
    if(meta2['f'] == 'Hometime' or meta2['f'] == 'Significant Location'):
        data2 = sigLocExtract(meta2)
    return jsonify([data1,data2])

def surveyPCA(meta):
    df = pd.read_csv(surveyFilePath+meta['pid']+'.csv')
    pdf = pd.DataFrame()
    pdf['ActivityDate'] = pd.to_datetime(df['ActivityDate'],dayfirst=True)
    categories = meta['f_opt']
    for category in categories:
        columnSubSet = []
        for column in list(df.columns):
            if(column[:-1] == category):
                columnSubSet.append(column)
        data = df[columnSubSet].values
        pca = PCA(n_components=1)
        pData = pca.fit_transform(data)
        pVal = pData[:,[0]]
        pVal = [val[0] for val in pVal]
        pdf[category] = pVal
    pdf['ActivityDate'] = pdf['ActivityDate'].dt.strftime("%d/%m/%Y")
    returnData = []
    vizMeta = {}
    for i in range(len(categories)):
        vizMeta['c'+str(i)] = categories[i]
    vizMeta['panelId'] = meta['panelId']
    returnData.append(vizMeta)
    for idx, row in pdf.iterrows():
        dic = {}
        dic['ActivityDate'] = row['ActivityDate'] #Constant column
        for column in categories:
            dic[column] = row[column]
        returnData.append(dic)
    return returnData

#Meta format - [Aggregate/Complete, Number of clusters]
def surveyPerformance(meta):
    df = pd.read_csv(surveyFilePath+meta['pid']+'.csv')
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'],dayfirst=True)
    df['ActivityDate'] = df['ActivityDate'].dt.strftime("%d/%m/%Y")
    #Aggregating features
    if(meta['f_opt'][0] == "Aggregate"):
        df["social"] = (df['social1'] + df['social2'] + df['social3'] + df['social4'] + df['social5'])/5
        df["mood"] = (df['mood1'] + df['mood2'] + df['mood3'] + df['mood4'] + df['mood5'] + df['mood6'] + df['mood7'] + df['mood8'] + df['mood9'])/9
        df["sleep"] = (df["sleep1"] +  df["sleep2"] + df["sleep3"])/3
        df["psychosis"] = (df['psychosis1'] + df['psychosis2'] + df['psychosis3'] + df['psychosis4'] + df['psychosis5'])/5
        df["anxiety"] = (df['anxiety1'] + df['anxiety2'] + df['anxiety3'] + df['anxiety4'] + df['anxiety5'] + df['anxiety6'] + df['anxiety7'])/7
    data = df.drop(columns=["ActivityDate"]).to_numpy()
    days = df.shape[0]
    matrixDat = np.zeros((days,days))
    if(meta['f_opt'][1] == "Natural"):
        save_stdout = sys.stdout
        sys.stdout = open('trash', 'w')
        model = AffinityPropagation(damping=0.5)
        matrixDat += co_association_matrix(model, data, days)
        model = DBSCAN(eps=0.1, min_samples=3)
        matrixDat += co_association_matrix(model, data, days)
        model = MeanShift()
        matrixDat += co_association_matrix(model, data, days)
        model = OPTICS(eps=0.1, min_samples=3)
        matrixDat += co_association_matrix(model, data, days)
        matrixDat /= 4.0
        sys.stdout = save_stdout
    else:
        print("second")
        print(data)
        save_stdout = sys.stdout
        try:
            print("thirdd")
            clusters = int(meta['f_opt'][1])
            # sys.stdout = open('trash', 'w')
            model = AgglomerativeClustering(n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            print(matrixDat)
            model = Birch(threshold=0.01, n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            print(matrixDat)
            model = KMeans(n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            print(matrixDat)
            model = MiniBatchKMeans(n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            print(matrixDat)
            model = SpectralClustering(n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            print(matrixDat)
            model = GaussianMixture(n_components=clusters)
            matrixDat += co_association_matrix(model, data, days)
            print(matrixDat)
            matrixDat /= 6.0
            # sys.stdout = save_stdout
            print("fourth")
        except:
            print("Couldn't convert string to int")
    
    print(matrixDat)
    returnData = [{'panelId':meta['panelId']},{'dates':list(df['ActivityDate'].values)},{'data': list(matrixDat.flatten())}]
    # print("Hi",returnData)
    return returnData

@app.route('/surveydata')
def surveyViz():
    data1 = []
    data2 = []
    if(meta1['f'] == 'Survey PCA'):
        data1 = surveyPCA(meta1)
    elif(meta1['f'] == 'Survey Performance'):
        data1 = surveyPerformance(meta1)
    if(meta2['f'] == 'Survey PCA'):
        data2 = surveyPCA(meta2)
    elif(meta2['f'] == 'Survey Performance'):
        data2 = surveyPerformance(meta2)        
    # print("hello",data1, data2)
    return jsonify([data1,data2])