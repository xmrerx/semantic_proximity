import json
import logging
import sys  # noqa
from enum import IntEnum
from time import time

import numpy as np
from gensim.models import Word2Vec
from scipy.spatial import distance

from utils.conf import Conf
from utils.file_nav import walk_sentences, walk_sentences_simple
from train_utils.util import doc_vec


DOCS_LIMIT = 1000000000


W2V_Alg = IntEnum('W2V_Alg', 'dbow sg')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    start_time = time()

    conf = Conf.get(__file__, 'config.ini')

    train_lemm = json.loads(conf.TRAIN['train_lemm'])
    # train_lemm = ['nltk', 'spacy']

    logging.info(f"use {DOCS_LIMIT} docs")
    for lemm in train_lemm:
        logging.info(f"lemm: {lemm}")

        sentences = list(walk_sentences_simple(
            conf.path('train', lemm), conf.APP['ext'], stop=DOCS_LIMIT
        ))
        for alg in W2V_Alg:
            logging.info(f"alg: {alg.name}; vec: {conf.TRAIN['vector_size']}; "
                         f"epochs {conf.TRAIN['epochs']}; alpha: {conf.TRAIN['alpha']}")
            model = Word2Vec(
                sentences,
                size=int(conf.TRAIN['vector_size']),
                iter=int(conf.TRAIN['epochs']),
                sg=alg,
                min_count=1
            )
            model.train(
                sentences=sentences,
                total_examples=len(sentences),
                epochs=model.iter
            )
            model.save(str(conf.path('train', f"w2v-{alg.name}-{lemm}.model")))

        sentences_map = walk_sentences(
            conf.path('train', lemm), conf.APP['ext'], stop=DOCS_LIMIT
        )
        vecs = []
        names = []
        vec = None
        for sentence_map in sentences_map:
            file_id, line_id, words = sentence_map
            vec = doc_vec(model, words)
            # vecs[f"{file_id} {line_id}"] = vec
            vecs.append(list(vec))
            names.append(f"{file_id} {line_id}")

        # print(np.array(vecs), np.array([list(vec)]))

        res = distance.cdist(np.array(vecs), np.array([list(vec)]), 'cosine')

        print(res[-5:])

        # res = np.sort(res, axis=None)

        # merged = []
        # for name in names:
        #     merged.append()
        # print(np.join(np.array(names), res))

        break
