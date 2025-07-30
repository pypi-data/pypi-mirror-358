

import os
import shlex
import sys
from os.path import abspath, dirname, exists as pexists, join as pjoin
from sys import version_info

sys.dont_write_bytecode = True

if __name__ == '__main__' and __package__ is None:
    parent_dir = dirname(dirname(abspath(__file__)))
    sys.path.append(parent_dir)

if version_info.major > 2:
    from neuropredict.classify import cli
else:
    raise NotImplementedError('neuropredict supports only Python 3+.')

max_num_classes = 10
max_class_size = 40
max_dim = 100
num_repetitions = 20
min_rep_per_class = 20

train_perc = 0.5
red_dim = 'sqrt'
classifier = 'randomforestclassifier' # 'svm' # 'extratreesclassifier'
fs_method = 'variancethreshold' # 'selectkbest_f_classif'
gs_level = 'none' # 'light'

num_procs = 1

base_dir = '/Volumes/data/work/rotman/CANBIND/gmdenisty_graynet'
ds_path = pjoin(base_dir, 'spm_cat_gmdensity_manhattan.MLDataset.pkl')
out_dir = pjoin(base_dir, 'trial_retrain_best_model_on_all_train_data')
if not pexists(out_dir):
    os.makedirs(out_dir)

sg_list = 'Responder,NonResponder'

sys.argv = shlex.split('neuropredict -y {} -t {} -n {} -c {} -g {} -o {} '
                       '-e {} -fs {} -sg {}'
                       ''.format(ds_path, train_perc, num_repetitions, num_procs,
                                 gs_level, out_dir, classifier, fs_method, sg_list))
cli()
