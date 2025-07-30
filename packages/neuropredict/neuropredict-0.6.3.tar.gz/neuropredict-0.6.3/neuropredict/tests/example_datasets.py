
import os
from os.path import dirname, join as pjoin

import numpy as np

test_dir = dirname(os.path.realpath(__file__))
example_data_dir = pjoin(dirname(dirname(test_dir)), 'example_datasets', 'pyradigm')

from sklearn.datasets import load_diabetes, load_boston, fetch_california_housing, \
    load_breast_cancer, fetch_lfw_people, fetch_lfw_pairs, fetch_covtype, fetch_kddcup99

from pyradigm import RegressionDataset, ClassificationDataset


def to_pyradigm(in_ds, feat_indices, ds_name, out_path, typ='regr'):
    """"""

    feat_names = np.array(in_ds.feature_names)

    if typ == 'regr':
        out_ds = RegressionDataset()
    else:
        out_ds = ClassificationDataset()
    out_ds.description = ds_name # in_ds.DESCR
    for ix in range(in_ds.data.shape[0]):
        out_ds.add_samplet(samplet_id=str(ix),
                           features=in_ds.data[ix, feat_indices],
                           target=in_ds.target[ix],
                           feature_names=feat_names[feat_indices])
    out_ds.save(out_path)

    return out_ds

def split_sklearn_ds(skl_ds, name='sklds', indices_fs1_perc=0.5, typ='regr'):

    tot_num_feat = skl_ds.data.shape[1]
    feat_indices = np.random.randint(0, tot_num_feat,
                                     int(indices_fs1_perc*tot_num_feat))
    suffix = '{}_rnf{}'.format(name, len(feat_indices))
    out_path = pjoin(example_data_dir, '{}.pkl'.format(suffix))
    ds = to_pyradigm(skl_ds, feat_indices, suffix, out_path, typ=typ)
    return ds


# -----

bc = load_breast_cancer()
bc.target = bc.target_names[bc.target]
split_sklearn_ds(bc, 'breast_cancer1', 0.5, typ='clf')
split_sklearn_ds(bc, 'breast_cancer2', 0.3, typ='clf')

# lfw_pairs = fetch_lfw_pairs()
# split_sklearn_ds(lfw_pairs, 'lfw_pairs1', 0.5)
# split_sklearn_ds(lfw_pairs, 'lfw_pairs2', 0.4)

lfw_people = fetch_lfw_people()
split_sklearn_ds(lfw_people, 'lfw_pairs1', 0.5, typ='clf')
split_sklearn_ds(lfw_people, 'lfw_pairs2', 0.4, typ='clf')

covtype = fetch_covtype()
split_sklearn_ds(covtype, 'covtype1', 0.6, typ='clf')
split_sklearn_ds(covtype, 'covtype2', 0.4, typ='clf')

kddcup99 = fetch_kddcup99()
split_sklearn_ds(kddcup99, 'kddcup991', 0.6, typ='clf')
split_sklearn_ds(kddcup99, 'kddcup992', 0.4, typ='clf')

# -----

calif = fetch_california_housing()

feat_indices = list(range(4))
out_path = pjoin(example_data_dir, 'california_f1to4.pkl')
CalifDs1 = to_pyradigm(calif, feat_indices, 'California f1to4', out_path)

feat_indices = list(range(4, 8))
out_path = pjoin(example_data_dir, 'california_f5to8.pkl')
CalifDs2 = to_pyradigm(calif, feat_indices, 'California f5to8', out_path)

# -----

diabetes = load_diabetes()

feat_indices = list(range(5))
out_path = pjoin(example_data_dir, 'diabetes_f1to5.pkl')
DiabDs1 = to_pyradigm(diabetes, feat_indices, 'Diabetes f1to5', out_path)

feat_indices = list(range(5, 10))
out_path = pjoin(example_data_dir, 'diabetes_f6to10.pkl')
DiabDs2 = to_pyradigm(diabetes, feat_indices, 'Diabetes f6to10', out_path)


# -----

boston = load_boston()

feat_indices = list(range(5))
out_path = pjoin(example_data_dir, 'boston_f1to5.pkl')
BostonDs1 = to_pyradigm(boston, feat_indices, 'Boston f1to5', out_path)

feat_indices = list(range(5, 13))
out_path = pjoin(example_data_dir, 'boston_f6to13.pkl')
BostonDs2 = to_pyradigm(boston, feat_indices, 'Boston f6to13', out_path)

print()