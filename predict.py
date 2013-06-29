import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import KFold
from sklearn.metrics import roc_curve, auc, precision_score, classification_report
import pickle
import pylab as pl
from scipy import interp
from sklearn.preprocessing import balance_weights

DATA_FPATH = "data/training.csv"
SAMPLING_NUM = 3620
TREE_NUM = 200

def randomforest(data, targets, tree_num=TREE_NUM):
    model = RandomForestClassifier(n_estimators=tree_num, 
                                   n_jobs=4, 
                                   max_features=data.shape[1]/2+1, 
                                   verbose=0, 
                                   compute_importances=True)
    model.fit(data, targets)
    return model

def weighted_randomforest(data, targets, tree_num=TREE_NUM):
    model = RandomForestClassifier(n_estimators=tree_num, 
                                   n_jobs=4, 
                                   max_features=data.shape[1]/2+1, 
                                   verbose=0, 
                                   compute_importances=True) 
    model.fit(data, targets, balance_weights(targets))
    return model

def get_sampling_training():
    df = pd.read_csv(DATA_FPATH, header=0, index_col=0)
    neg_df = df[df['success']==0]
    pos_df = df[df['success']==1]
    
    rows = np.random.choice(neg_df.index.values, SAMPLING_NUM)
    sampled_neg_df = df.ix[rows]
    
    new_df = pd.concat([pos_df, sampled_neg_df])
    return new_df

def get_training_data():
    df = pd.read_csv(DATA_FPATH, header=0, index_col=0)
    return df

def validation():
    #df = get_training_data()
    df = get_sampling_training()

    targets = np.array(df['success'])
    del df['success']
    del df['name']
    data = np.array(df)
    kf = KFold(data.shape[0], n_folds=5, shuffle=True)
    for train_index, test_index in kf:
        model = randomforest(data[train_index], targets[train_index], tree_num=TREE_NUM)
        #model = weighted_randomforest(data[train_index], targets[train_index], tree_num=TREE_NUM)
        
        predictions = model.predict(data[test_index])
        #print precision_score(targets[test_index], predictions)
        print classification_report(targets[test_index], predictions)

def generate_roc():
    #df = get_training_data()
    df = get_sampling_training()
    
    targets = np.array(df['success'])
    del df['success']
    del df['name']
    data = np.array(df)
    kf = KFold(data.shape[0], n_folds=5, shuffle=True)
    
    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    for train_index, test_index in kf:
        model = randomforest(data[train_index], targets[train_index], tree_num=TREE_NUM)
        probas_ = model.predict_proba(data[test_index])
        fpr, tpr, thresholds = roc_curve(targets[test_index], probas_[:, 1])
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        roc_auc = auc(fpr, tpr)
    mean_tpr /= len(kf)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    pl.plot(mean_fpr, mean_tpr, label='Mean AUC = %0.2f' % mean_auc, lw=2)

    pl.xlim([-0.05, 1.05])
    pl.ylim([-0.05, 1.05])
    pl.xlabel('False Positive Rate')
    pl.ylabel('True Positive Rate')
    pl.title('Mean ROC Curve')
    pl.legend(loc="lower right")
    pl.savefig('plots/sampling_mean_roc.pdf')
    pl.show()

def build_model():
    #df = get_training_data()
    df = get_sampling_training()

    targets = np.array(df['success'])
    del df['success']
    del df['name']
    
    columns = df.columns

    data = np.array(df)
    model = randomforest(data, targets, tree_num=200)
    
    for ind, v in enumerate(model.feature_importances_):
        print columns[ind], v

    pickle.dump(model, open("data/rf.model", "w"))

def main():
    #generate_roc()
    
    #validation()
    
    build_model()


if __name__ == "__main__":
    main()

