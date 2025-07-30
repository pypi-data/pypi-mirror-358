from pyradigm import MLDataset, MultiOutputMLDataset
from pyradigm.utils import make_random_MLdataset
import os, sys
import numpy as np
from os.path import join as pjoin, exists as pexists, realpath, basename, dirname, isfile

sys.dont_write_bytecode = True
from pytest import raises, warns

a = MLDataset(filepath='/Volumes/data/work/rotman/CANBIND/data/Tier1_v1/processing/'
                       'IndivSymptoms_CANBIND_Tier1_MultiModal_features'
                       '.KeepNaN.MultiOutputMLDataset.pkl')

min_num_modalities = 3
max_num_modalities = 10
max_feat_dim = 10

num_classes  = np.random.randint( 2, 10)
class_sizes  = np.random.randint(10, 100, num_classes)
num_features = np.random.randint(5, 20)

# multi-output: target is a vector!
num_outputs_per_subject = 10
# range of labels for any given subject
output_set = np.arange(0, 7, dtype='int8')

def make_labels(seed):
    """Generates a random vector of labels."""

    return np.random.choice(output_set, num_outputs_per_subject)

class_set    = np.array([ f'C{x:05d}' for x in range(num_classes)])
feat_names   = np.array([ str(x) for x in range(num_features) ])

test_dataset = MultiOutputMLDataset(num_outputs=num_outputs_per_subject)
for class_index, class_id in enumerate(class_set):
    for sub_ix in range(class_sizes[class_index]):
        subj_id = f'{class_set[class_index]}_S{sub_ix:05d}'
        feat = np.random.random(num_features)
        test_dataset.add_samplet(subj_id, feat, make_labels(class_index),
                                 feature_names=feat_names)

dat, lbl, ids = test_dataset.data_and_targets()

out_dir = '.'
out_file = os.path.join(out_dir,'random_example_dataset.pkl')
test_dataset.save(out_file)

reloaded = MultiOutputMLDataset(filepath=out_file)

print()