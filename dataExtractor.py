import pandas as pd
from sklearn.decomposition import PCA
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
from helperFuncs import co_association_matrix
import numpy as np
import sys

def sigLocExtract(sigLocFilePath, meta):
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

def surveyPCA(surveyFilePath, meta):
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
def surveyPerformance(surveyFilePath, meta):
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
        save_stdout = sys.stdout
        try:
            clusters = int(meta['f_opt'][1])
            sys.stdout = open('trash', 'w')
            model = AgglomerativeClustering(n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            model = Birch(threshold=0.01, n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            model = KMeans(n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            model = MiniBatchKMeans(n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            model = SpectralClustering(n_clusters=clusters)
            matrixDat += co_association_matrix(model, data, days)
            model = GaussianMixture(n_components=clusters)
            matrixDat += co_association_matrix(model, data, days)
            matrixDat /= 6.0
            sys.stdout = save_stdout
        except:
            print("Couldn't convert string to int")
    returnData = [{'panelId':meta['panelId']},{'dates':list(df['ActivityDate'].values)},{'data': list(matrixDat.flatten())}]
    # print("Hi",returnData)
    return returnData            