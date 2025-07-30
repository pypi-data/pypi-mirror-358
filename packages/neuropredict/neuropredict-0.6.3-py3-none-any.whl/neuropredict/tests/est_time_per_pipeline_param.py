import itertools
import pickle
import time
from multiprocessing import Pool
from os.path import join as pjoin, realpath

import numpy as np
from neuropredict import rhst
from neuropredict.rhst import optimize_pipeline_via_grid_search_CV as opt_gs
from pyradigm import MLDataset
from sklearn.datasets import make_classification as make_toy_data

train_perc      = 0.8
n_trials        = 5 # for better estimates
n_features      = 1000
n_classes       = 2
n_samples       = 500
n_informative   = 15
class_sep       = 1.0

out_dir=realpath('.')
out_name = 'elapsed_times_nc{n_classes}_ns{n_samples}_nf{n_features}_rep{n_trials}.pkl'.format(n_classes=n_classes,
                                                                                               n_samples=n_samples,
                                                                                               n_features=n_features,
                                                                                               n_trials=n_trials)

data_mat = list()
labels = list()
for trial in range(n_trials):
    mat, lbl = make_toy_data(n_classes=n_classes,
                             n_samples=n_samples,
                             n_features=n_features,
                             n_informative=n_informative,
                             class_sep=class_sep)
    data_mat.append(mat)
    labels.append(lbl)

ds = MLDataset()
for ix, lbl in enumerate(labels[0]):
    ds.add_sample(sample_id=ix, features=data_mat[0][ix,:],
                  label=ix, class_id=str(ix))

train_class_sizes = list(ds.class_sizes.values())
feat_sel_size = np.sqrt(np.sum(train_class_sizes))

# ds.save(pjoin(out_dir,'toy.MLDataset.pkl'))

pipeline, param_grid = rhst.get_pipeline(train_class_sizes, feat_sel_size, n_features)

range_num_trees     = [50, 200, 500]
split_criteria      = ['gini', 'entropy']
range_min_leafsize  = [1, 3, 5, 9]
range_min_impurity  = [0.01, 0.001, 0.1]
range_max_features  = ['sqrt', 'log2', 0.25, 0.4]
exhaust_combination = itertools.product(range_num_trees, range_min_impurity,
                                        range_max_features, split_criteria)

param_grid_list_dict = [{'random_forest_clf__n_estimators': [n_estimators, ],
                         'random_forest_clf__min_impurity_decrease': [min_impurity_decrease, ],
                         'random_forest_clf__max_features': [max_features, ],
                         'random_forest_clf__criterion': [criterion, ]
                         }
                        for (n_estimators, min_impurity_decrease,
                             max_features, criterion)
                        in exhaust_combination
                        ]

def time_one_run(trial):
    ""
    start=time.time()
    ignored = opt_gs(pipeline, data_mat[trial], labels[trial], param, train_perc)
    end=time.time()
    elapsed=end-start

    return elapsed

exec_time = list()
median_exec_time_per_trial=list()
for param in param_grid_list_dict:
    print(param)
    with Pool(processes=n_trials) as pool:
        elapsed = pool.map(time_one_run, range(n_trials))

    median_exec_time=np.nanmedian(elapsed)
    print('\telapsed time: {}'.format(median_exec_time))
    median_exec_time_per_trial.append(median_exec_time)
    exec_time.append(elapsed)

with open(pjoin(out_dir,out_name), 'w') as ef:
    pickle.dump([param_grid_list_dict, exec_time], ef)
