import numpy as np

def co_association_matrix(model, X, days):
    matrix = np.zeros((days, days))
    yhat = model.fit_predict(X)
    clusters = np.unique(yhat)
    print("--------------------------------------------------")
    print(model.__class__)
    print("number of clusters: " + str(len(clusters)))

    for cluster in clusters:
        row_ix = np.where(yhat == cluster)[0]
        print(row_ix)
        for i in row_ix:
            for j in row_ix:
                matrix[i-1][j-1] = 1
    return matrix