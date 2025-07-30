

import os
import shlex
import sys
from os.path import abspath, dirname, exists as pexists
from sys import version_info

sys.dont_write_bytecode = True

if __name__ == '__main__' and __package__ is None:
    parent_dir = dirname(dirname(abspath(__file__)))
    sys.path.append(parent_dir)

if version_info.major > 2:
    from neuropredict import cli
else:
    raise NotImplementedError('neuropredict supports only Python 3+.')

out_dir = os.path.abspath('../tests/scratch')
if not pexists(out_dir):
    os.makedirs(out_dir)

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


def test_multi_output_dataset():

    multi_output_path = '/Volumes/data/work/rotman/CANBIND/data/Tier1_v1/processing/' \
                        'IndivSymptoms_CANBIND_Tier1_MultiModal_features' \
                        '.KeepNaN.MultiOutputMLDataset.pkl'
    sys.argv = shlex.split('neuropredict -y {} -t {} -n {} -c {} -g {} -o {} '
                           '-e {} -fs {} -is median'
                           ''.format(multi_output_path, train_perc,
                                     num_repetitions, num_procs, gs_level, out_dir,
                                     classifier, fs_method))
    cli()
