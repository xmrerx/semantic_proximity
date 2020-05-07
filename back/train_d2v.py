import json
import logging
import pathlib
import sys  # noqa
import typing as t
from enum import IntEnum
from random import shuffle
from time import time

from gensim.models.doc2vec import Doc2Vec, TaggedDocument

from utils.conf import Conf
from utils.file_nav import walk_sentences


DOCS_LIMIT = 1000000000


def walk_sentences_as_tagged_doc(
    source_dir: pathlib.Path,
    ext: str,
    *,
    stop: t.Optional[int] = None,
    without_file: t.Optional[str] = None,
    split_line: bool = True
) -> t.List:
    for sentence_map in walk_sentences(**locals()):
        file_id, line_id, words = sentence_map
        yield TaggedDocument(words=words, tags=[f"{file_id} {line_id}"])


D2V_Alg = IntEnum('D2V_Alg', 'dbow dm')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    start_time = time()

    conf = Conf.get(__file__, 'config.ini')

    train_lemm = json.loads(conf.TRAIN['train_lemm'])
    train_lemm = ['nltk', 'spacy']

    logging.info(f"use {DOCS_LIMIT} docs")
    for lemm in train_lemm:
        logging.info(f"lemm: {lemm}")
        tagged_sentences = list(walk_sentences_as_tagged_doc(
            conf.path('train', lemm), conf.APP['ext'], stop=DOCS_LIMIT
        ))
        for alg in D2V_Alg:
            logging.info(f"alg: {alg.name}; vec: {conf.TRAIN['vector_size']}; "
                         f"epochs {conf.TRAIN['epochs']}; alpha: {conf.TRAIN['alpha']}")
            model = Doc2Vec(  # dbow_words for dbow?
                vector_size=int(conf.TRAIN['vector_size']),
                epochs=int(conf.TRAIN['epochs']),
                alpha=float(conf.TRAIN['alpha']),
                min_alpha=float(conf.TRAIN['min_alpha']),
                dm=alg
            )
            model.build_vocab(tagged_sentences)
            shuffled_tagged_sentences = tagged_sentences[:]
            shuffle(shuffled_tagged_sentences)
            model.train(
                shuffled_tagged_sentences,
                total_examples=model.corpus_count,
                epochs=model.epochs
            )
            model.save(str(conf.path('train', f"d2v-{alg.name}-{lemm}.model")))
