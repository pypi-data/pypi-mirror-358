import shlex
import sys
from os import makedirs, listdir
from os.path import join as pjoin
import fnmatch
from neuropredict.classify import cli as run_cli

base_dir = '/Volumes/work/rotman/CANBIND/cohort_info/covariates/' \
           'thk_curv_sulc_area_fsaverage_fwhm10_nbins25_NewDatasets'

ds_paths = (pjoin(base_dir, fp) for fp in
            fnmatch.filter(listdir(base_dir), '*intersec*.pkl'))
ds_paths = ' '.join(ds_paths)

positive_class = 'Responder'

clf = 'randomforestclassifier'
fs_method = 'isomap'
feat_sel_size = 'tenth'
gsl = 'light'  # to speed up the process

cov_spec = ' -cl age sex site -cm Residualize '

num_rep = 20
train_perc = 0.8
num_cpus = 1

suffix = '{}_{}_k_{}_gsl_{}_tp{}_n{}' \
         ''.format(clf, fs_method, feat_sel_size, gsl, train_perc, num_rep)
out_dir = pjoin(base_dir, '_np_{}'.format(suffix))

makedirs(out_dir, exist_ok=True)

cli_str = 'np_classify -y {dp} -o {od} -p {pc} -e {clf} -dr {fsm} {covspec}-k ' \
          '{fs} -n {nr} -t {tp} -g {gs} -c {numcpu}' \
          ''.format(dp=ds_paths, od=out_dir,
                    clf=clf, fsm=fs_method, gs=gsl, covspec=cov_spec,
                    nr=num_rep, tp=train_perc, fs=feat_sel_size,
                    pc=positive_class, numcpu=num_cpus)

sys.argv = shlex.split(cli_str)

run_cli()
