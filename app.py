from email import message
from os import stat
from attr import dataclass
from flask import Flask,render_template,request,session,jsonify
import csv
import pandas as pd
import numpy as np
import pickle
from os.path import exists
from dataExtractor import sigLocExtract, surveyPCA, surveyPerformance

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

@app.route('/sigLocdata')
def sigLocdata():
    data1 = []
    data2 = []
    if(meta1['f'] == 'Hometime' or meta1['f'] == 'Significant Location'):
        data1 = sigLocExtract(sigLocFilePath, meta1)
    if(meta2['f'] == 'Hometime' or meta2['f'] == 'Significant Location'):
        data2 = sigLocExtract(sigLocFilePath, meta2)
    return jsonify([data1,data2])

@app.route('/surveydata')
def surveyViz():
    data1 = []
    data2 = []
    if(meta1['f'] == 'Survey PCA'):
        data1 = surveyPCA(surveyFilePath, meta1)
    elif(meta1['f'] == 'Survey Performance'):
        data1 = surveyPerformance(surveyFilePath, meta1)
    if(meta2['f'] == 'Survey PCA'):
        data2 = surveyPCA(surveyFilePath, meta2)
    elif(meta2['f'] == 'Survey Performance'):
        data2 = surveyPerformance(surveyFilePath, meta2)        
    return jsonify([data1,data2])