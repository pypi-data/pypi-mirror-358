
import os
from os.path import abspath, dirname, exists as pexists, join as pjoin, realpath
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from matplotlib.backends.backend_pdf import PdfPages
from neuropredict import config as cfg
from neuropredict.visualize import vis_single_confusion_matrix, mean_over_cv_trials

test_dir = dirname(os.path.realpath(__file__))
out_dir = realpath(pjoin(test_dir, '..', 'tests', 'cmap_selection_trials'))
if not pexists(out_dir):
    os.makedirs(out_dir)

cmaps = OrderedDict()

cmaps['Perceptually Uniform Sequential'] = [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis']

cmaps['Sequential'] = [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']

cmaps['Sequential (2)'] = [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']

cmaps['Diverging'] = [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']

seq = cmaps['Perceptually Uniform Sequential'] + cmaps['Sequential']
num_cmaps = len(seq)

class_labels=('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', "I")

def conf_per_class(nc):
    """Confusion matrix of size nc x nc"""
    arr = np.random.rand(nc)
    return arr / arr.sum()

for num_classes in (3, 4, 2, 5, 6, 7):
    cur_dir = pjoin(out_dir, 'num_classes_{}'.format(num_classes))
    os.makedirs(cur_dir, exist_ok=True)

    for trial in range(5):

        fig, axes = plt.subplots(4, 6, figsize=(24, 24))
        axes = axes.flatten()

        cf_mat = np.vstack([conf_per_class(num_classes) for _ in range(num_classes)])
        for idx, cmap in enumerate(seq):
            vis_single_confusion_matrix(100*cf_mat,
                                        title=cmap, cmap=cmap, ax=axes[idx],
                                        class_labels=class_labels)

        for ax in axes[idx+1:]:
            ax.remove()

        output_path = pjoin(cur_dir, 'cmap_sel_nc{}_trial{}.png'
                                     ''.format(num_classes, trial))
        fig.tight_layout()
        # fig.savefig(output_path)
        fig.savefig(output_path, orientation='landscape')
        # pp1 = PdfPages(output_path)
        # pp1.savefig()
        # pp1.close()
        plt.close()
        print('NC {} trial {} done'.format(num_classes, trial))