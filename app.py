from attr import dataclass
from flask import Flask,render_template,request,session,jsonify
import csv
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from scipy.interpolate import make_interp_spline
import pickle

app = Flask(__name__) #create app instance
app.secret_key = 'example' #store this in an environment variable for live apps.
filepath = 'input/'
req = ['mood']
meta1 = {'columns':['mood'],'panelId':'#panel1Viz','pid':"U1606505063",'dependency':{}}
meta2 = {'columns':['mood'],'panelId':'#panel2Viz','pid':"U7744128165"}

#homepage
@app.route('/')
def index():
    return render_template('home.html')

def dataExtractor():
    p1 = meta1['pid']
    print(meta1['columns'])
    df = pd.read_csv('input/features_'+p1+'.csv')
    pdf = pd.DataFrame()
    pcaList = []
    pdf['ActivityDate'] = pd.to_datetime(df['ActivityDate'],dayfirst=True)
    categories = ['mood','sleep','anxiety','psychosis','social']
    for category in categories:
        columnSubSet = []
        for column in list(df.columns):
            if(column[:-1] == category):
                columnSubSet.append(column)
        data = df[columnSubSet].values
        print(category,np.shape(data))
        pca = PCA(n_components=1)
        pData = pca.fit_transform(data)
        pcaList.append(pca)
        pVal = pData[:,[0]]
        pVal = [val[0] for val in pVal]
        pdf[category] = pVal
    pdf['ActivityDate'] = pdf['ActivityDate'].dt.strftime("%d/%m/%Y")
    data1 = []
    meta = {}
    columns = meta1['columns']
    for i in range(len(columns)):
        meta['c'+str(i)] = columns[i]
    meta['panelId'] = meta1['panelId']
    data1.append(meta)
    print(list(pdf.columns))
    for idx, row in pdf.iterrows():
        dic = {}
        dic['ActivityDate'] = row['ActivityDate'] #Constant column
        for column in columns:
            dic[column] = row[column]
        data1.append(dic)
    p2 = meta2['pid']
    df = pd.read_csv('input/features_'+p2+'.csv')
    pdf = pd.DataFrame()
    pdf['ActivityDate'] = pd.to_datetime(df['ActivityDate'],dayfirst=True)
    for category, pca in zip(categories,pcaList):
        columnSubSet = []
        for column in list(df.columns):
            if(column[:-1] == category):
                columnSubSet.append(column)
        data = df[columnSubSet].values
        pData = pca.transform(data)
        pVal = pData[:,[0]]
        pVal = [val[0] for val in pVal]
        pdf[category] = pVal
    pdf['ActivityDate'] = pdf['ActivityDate'].dt.strftime("%d/%m/%Y")
    data2 = []
    meta = {}
    columns = meta1['columns']
    for i in range(len(columns)):
        meta['c'+str(i)] = columns[i]
    meta['panelId'] = meta2['panelId']
    data2.append(meta)
    for idx, row in pdf.iterrows():
        dic = {}
        dic['ActivityDate'] = row['ActivityDate'] #Constant column
        for column in columns:
            dic[column] = row[column]
        data2.append(dic)

    return [data1,data2]

@app.route('/survey', methods=['GET','POST'])
def surveyInteraction():
    if request.method == 'POST':
        cols = request.form.getlist('p2SurveyCols')
        print(cols)
        if(len(cols) != 0):
            meta1['columns'] = cols
        else:
            meta1['columns'] = ['mood']
    meta2['columns'] = meta1['columns']
    return render_template('survey.html', ticked=meta2['columns'])
    

@app.route('/panel1Survey', methods=['GET','POST'])
def panel1Survey():
    data = dataExtractor()[0]
    return jsonify(data)

@app.route('/panel2Survey', methods=['GET','POST'])
def panel2Survey():
    # patientId = meta2['pid']
    # df = pd.read_csv('input/features_'+patientId+'.csv')
    # pdf = pd.DataFrame()
    # pdf['ActivityDate'] = pd.to_datetime(df['ActivityDate'],dayfirst=True)
    # for category in meta2['columns']:
    #     columnSubSet = []
    #     for column in list(df.columns):
    #         if(column[:-1] == category):
    #             columnSubSet.append(column)
    #     data = df[columnSubSet].values
    #     pca = PCA(n_components=1)
    #     pData = pca.fit_transform(data)
    #     pVal = pData[:,[0]]
    #     pVal = [val[0] for val in pVal]
    #     pdf[category] = pVal
    # pdf['ActivityDate'] = pdf['ActivityDate'].dt.strftime("%d/%m/%Y")
    # data = []
    # meta = {}
    # columns = meta2['columns']
    # for i in range(len(columns)):
    #     meta['c'+str(i)] = columns[i]
    # meta['panelId'] = meta2['panelId']
    # data.append(meta)
    # for idx, row in pdf.iterrows():
    #     dic = {}
    #     dic['ActivityDate'] = row['ActivityDate'] #Constant column
    #     for column in columns:
    #         dic[column] = row[column]
    #     data.append(dic)
    data = dataExtractor()[1]
    return jsonify(data)
# @app.route("/", methods = ['GET','POST'])
# def H2H():
#     #set default form values
#     if request.form.get("squadA_select") == None:
#         Squad_a = 'Manchester City'
#     else:
#         Squad_a = request.form.get("squadA_select")
#     if request.form.get("squadB_select") == None:
#         Squad_b = 'Arsenal'
#     else:
#         Squad_b =request.form.get("squadB_select")

#     #get list of teams and selected teams to feed into html template
#     squads = pd.read_csv(filepath + 'squad_list.csv')
#     squad_list_a = list(squads.Squad) #just gets the squad list column
#     squad_list_b = list(squads.Squad)
#     Match = Squad_a +  ' vs. ' + Squad_b
#     session['Squad_a'] = Squad_a
#     session['Squad_b'] = Squad_b
#     session['Match'] = Match
#     return render_template("index.html",Squad_a = Squad_a, Squad_b = Squad_b,squad_list_a=squad_list_a, squad_list_b=squad_list_b , Match = Match)

@app.route("/data")
def get_data():
    Squad_a, Squad_b, Match = [session.get('Squad_a', None),session.get('Squad_b', None), session.get('Match', None)]

    df = player_df[(player_df.Squad == Squad_a) | (player_df.Squad == Squad_b)]
    df['Match'] = Match
    return df.to_json(orient='records')

@app.route("/formData")
def get_team_data():
    Squad_a, Squad_b, Match = [session.get('Squad_a', None),session.get('Squad_b', None), session.get('Match', None)]

    df = team_df[(team_df.Squad == Squad_a) | (team_df.Squad == Squad_b)]
    df['Match'] = Match

    return df.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True)