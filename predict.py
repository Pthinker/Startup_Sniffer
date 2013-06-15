import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import KFold
from sklearn.metrics import precision_score
from sklearn.metrics import classification_report
import pickle

def randomforest(data, targets, tree_num=100):
    model = RandomForestClassifier(n_estimators=tree_num, 
                                   n_jobs=4, 
                                   max_features=data.shape[1]/2+1, 
                                   verbose=0, 
                                   oob_score=True, 
                                   compute_importances=True, 
                                   random_state=12345678)
    model.fit(data, targets)
    return model

def validation():
    df = pd.read_csv("companies.csv", header=0, index_col=0)
    targets = np.array(df['success'])
    del df['success']
    data = np.array(df)
    kf = KFold(data.shape[0], k=5, shuffle=True)
    for train_index, test_index in kf:
        model = randomforest(data[train_index], targets[train_index], tree_num=100)
        probas_ = model.predict_proba(data[test_index])
        predictions = model.predict(data[test_index])
        #print precision_score(targets[test_index], predictions)
        #print classification_report(targets[test_index], predictions)

def build_model():
    df = pd.read_csv("companies.csv", header=0, index_col=0)
    targets = np.array(df['success'])
    del df['success']
    data = np.array(df)
    model = randomforest(data, targets, tree_num=100)
    pickle.dump(model, open("mobile.model", "w"))

def main():
    build_model()

if __name__ == "__main__":
    main()
