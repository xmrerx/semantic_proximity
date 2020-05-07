import json
import io
import logging
import sys  # noqa
import uuid
from time import time

import pandas as pd

from utils.path import nearby, File
from utils.text_manip import split_sentences
from utils.file_nav import get_offsets, save_content
from utils.conf import get_conf
from train_utils.util import split_using


def save_train(sentences, train_lemm, data_path, file):
    sent_lemm = {k: [] for k in train_lemm}
    for sentence in sentences:
        for lemm in train_lemm:
            words = split_using(sentence, lemm)
            sent_lemm[lemm].append(' '.join(words))

    for lemm in train_lemm:
        lemm_file_path = data_path[lemm].joinpath(file)
        save_content(lemm_file_path, sent_lemm[lemm])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    init_path = nearby(__file__, 'init_data')
    init_files = (File('True', 'csv'), File('Fake', 'csv'))

    conf = get_conf(__file__, 'config.ini')
    data_path = {
        'all_texts': nearby(__file__, conf.PATH['all_texts'])
    }
    train_lemm = json.loads(conf.TRAIN['train_lemm'])
    for lemm in train_lemm:
        data_path[lemm] = nearby(__file__, (conf.PATH['train'], lemm))

    start_time = time()

    metadata_list = []
    offsets_list = []
    for init_file_id, init_file in enumerate(init_files):
        df = pd.read_csv(init_path.joinpath(str(init_file)))

        logging.info(f"shape {df.shape}")

        for text_id, text in enumerate(df['text']):
            file_id = File(uuid.uuid4(), conf.APP['ext'])
            metadata_list.append({
                'group_id': init_file_id,
                'text_id': text_id,
                'file_id': file_id.name
            })
            sentences = split_sentences(text)
            if len(sentences):
                raw_sent_file_path = data_path['all_texts'].joinpath(str(file_id))
                with io.open(raw_sent_file_path, 'a+', encoding='utf8') as file:
                    file.write("\n".join(sentences))
                    offsets_list.append({
                        'file_id': file_id.name,
                        'offsets': get_offsets(file, 'utf8')
                    })
                save_train(sentences, train_lemm, data_path, str(file_id))
            break

    df_meta = pd.DataFrame(metadata_list)
    df_meta.to_pickle(nearby(__file__, (conf.PATH['train'], 'meta.pkl')))

    df_offsets = pd.DataFrame(offsets_list)
    df_offsets['file_id'] = df_offsets['file_id'].astype('str')
    df_offsets.set_index(['file_id'], inplace=True)
    df_offsets.to_pickle(nearby(__file__, (conf.PATH['train'], 'offsets.pkl')))
