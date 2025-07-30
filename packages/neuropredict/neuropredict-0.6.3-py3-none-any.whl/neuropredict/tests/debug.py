import os
import shlex
import sys
from neuropredict import cli

out_dir = '/Volumes/data/work/rotman/CANBIND/data/Tier1_v1/processing/multimodal'
os.chdir(out_dir)


# sys.argv = shlex.split('neuropredict -n 10 -t 0.8 -fs selectkbest_mutual_info_classif '
#                        '-y SubsetMultimodal_CANBIND_Tier1_Clinical_features.SkipSubjWithNaNVar.MLDataset.pkl '
#                        'SubsetMultimodal_CANBIND_Tier1_Molecular_features.SkipSubjWithNaNVar.MLDataset.pkl '
#                        'SubsetMultimodal_CANBIND_Tier1_Neuroimaging-DWI_features.SkipSubjWithNaNVar.MLDataset.pkl '
#                        'SubsetMultimodal_CANBIND_Tier1_Neuroimaging-T1w_features.SkipSubjWithNaNVar.MLDataset.pkl '
#                        '-o /Users/Reddy/rotman/CANBIND/data/Tier1_v1/processing/multimodal/np_SubsetMultimodal')

# sys.argv = shlex.split('neuropredict -n 10 -t 0.8 -fs selectkbest_mutual_info_classif '
#                        '-e svm '
#                        '-y SubsetMultimodal_CANBIND_Tier1_Clinical_features.SkipSubjWithNaNVar.MLDataset.pkl '
#                        '-o /Users/Reddy/rotman/CANBIND/data/Tier1_v1/processing/multimodal/np_SubsetMultimodal')

vis_dir = '/Volumes/data/work/rotman/CANBIND/data/Tier1_v1/processing/multimodal' \
          '/np_SubsetMultimodal_n100/NonResponder_Responder'
sys.argv = shlex.split('neuropredict --make_vis {}'.format(vis_dir))

cli()