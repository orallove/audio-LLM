import argparse
import glob
import logging
import os
import pickle
import random
import re
import shutil
from typing import Dict, List, Tuple

import numpy as np
import torch
from tqdm import tqdm, trange
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, Dataset, RandomSampler, SequentialSampler
from torch.utils.data.distributed import DistributedSampler

logger = logging.getLogger(__name__)


class AudioProcessor(Dataset):
    # Audio Speech Recognition Processor
    # get audio file name and text
    # example:
    # data_dir/61/70970/61-70970.trans.txt
    # 61-70970-0005 THE LAD HAD CHECKED HIM THEN
    # 
    # audio file name: 61-70970-0005.flac
    # audio file path: data_dir/61/70970/61-70970-0005.flac
    # text: THE LAD HAD CHECKED HIM THEN
    def __init__(self, data_dir):
        self.text_path_list = glob.glob(os.path.join(data_dir, '*', '*', '*.txt'))
        self.text_list = []
        self.audio_path_list = []
        for text_path in self.text_path_list:
            with open(text_path, 'r') as f:
                audio_path_pre = text_path.rsplit('/', 1)[0]
                for line in f.readlines():
                    line = line.strip()
                    if line != '':
                        self.text_list.append(line.split(' ', 1)[-1])
                        audio_path = audio_path_pre + '/' + line.split(' ', 1)[0] + '.flac'
                        self.audio_path_list.append(audio_path)

    
        
    def __len__(self):
        return len(self.audio_path_list)
    
    def __getitem__(self, idx):
        return self.audio_path_list[idx], self.text_list[idx]


def compute_metrics(preds, labels):
    assert len(preds) == len(labels)
    # return average word error rate
    return {"acc": (preds == labels).mean()}

    


def load_and_cache_audio_examples(args,data_type,evaluate=False):
    if data_type=='train':
        processor = processors["wave2text"](args.train_data_dir)
    elif data_type=='dev':
        processor = processors["wave2text"](args.dev_data_dir)
    else:
        processor = processors["wave2text"](args.test_data_dir)

    return processor


processors = {
    "wave2text": AudioProcessor,
}

output_modes = {
    "wave2text": "text"
}
# test train_dataset
# train_dataset = AudioProcessor("data-asr/LibriSpeech/test-clean")
# audio_train_dataloader = DataLoader(
#     train_dataset, batch_size=8
# )
# audio_epoch_iterator = tqdm(audio_train_dataloader, desc="Iteration")
# for step, batch in enumerate(audio_epoch_iterator):
#     print(batch[0])
