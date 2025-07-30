import shlex
import sys

from neuropredict.regress import cli

prog = 'np_regress'

out_dir = '/Users/Reddy/dev/neuropredict/neuropredict/tests/scratch_regress_backup'
# out_dir = '/Users/Reddy/dev/neuropredict/neuropredict/tests/scratch_classify'

# sys.argv = shlex.split('{} -z {}'.format(prog, out_dir))
sys.argv = shlex.split('{} --po {}'.format(prog, out_dir))

cli()

