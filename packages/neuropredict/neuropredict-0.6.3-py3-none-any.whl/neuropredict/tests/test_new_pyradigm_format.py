import shlex
import sys
from os import makedirs
from os.path import join as pjoin, exists as pexists

from neuropredict.classify import cli as run_cli

base_dir = '/Users/Reddy/dev/rotman-dev/TorCA'
method_list = ('TorCA', 'MoCA')
ds_paths = (pjoin(base_dir, '{}_classify.pyradigm.pkl'.format(method))
           for method in method_list)
ds_paths = ' '.join(ds_paths)

out_dir = pjoin(base_dir, 'np_test_trial')
makedirs(out_dir, exist_ok=True)

positive_class = 'MCI'

clf = 'randomforestclassifier'
gsl = 'None'  # to speed up the process

num_rep = 12
train_perc = 0.8
feat_sel_size = 'all'
num_cpus = 1

sys.argv = shlex.split('neuropredict -y {dp} -o {od} -p {pc} '
                       '-k {fs} -n {nr} -t {tp} -g {gs} -e {clf} -c {numcpu}'
                       ''.format(dp=ds_paths, od=out_dir, clf=clf, gs=gsl,
                                 nr=num_rep, tp=train_perc, fs=feat_sel_size,
                                 pc=positive_class, numcpu=num_cpus))

run_cli()

# from pytest import raises
# out_dir = pjoin(base_dir, 'np_trial1', 'MCI_control')
# res_path = pjoin(out_dir, 'rhst_results.pkl')
# if pexists(res_path):
#     with raises(SystemExit):
#         sys.argv = shlex.split('neuropredict --make_vis {}'.format(out_dir))
#         run_cli()