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
#read in data

df = pd.read_csv('input/features_U1606505063.csv')

#homepage
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/patientSurveyData')
def patientSurveyData():
    categories = ['social','mood','sleep','psychosis','anxiety']
    pdf = pd.DataFrame()
    pdf['ActivityDate'] = pd.to_datetime(df['ActivityDate'],dayfirst=True)
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
    # pdf['ActivityDate'] = pd.to_datetime(pd['ActivityDate'], dayfirst=True)
    tempDf = pdf.copy(deep=True)
    tempDf = tempDf.sort_values(by='ActivityDate')
    tempDf['ActivityDate'] = tempDf['ActivityDate'].dt.strftime("%d/%m/%Y")
    print(tempDf.head())
    columns = list(pdf.columns)
    data = []
    for idx, row in tempDf.iterrows():
        dic = {}
        for column in columns:
            dic[column] = row[column]
        data.append(dict(row))
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