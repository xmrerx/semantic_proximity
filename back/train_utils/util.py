import typing as t
from enum import Enum

import numpy as np

from utils.text_manip import extract_words, Lemmatizer


__all__ = [
    'Lemm',
    'split_using'
]


class Lemm(Enum):
    no = 'no'
    nltk = 'nltk'
    spacy = 'spacy'


def split_using(sentence: str, lemm: Lemm = Lemm.no) -> t.List:
    kwargs = {
        Lemm.no.value: {'clr_punct': False, 'clr_stop': False},
        Lemm.spacy.value: {'lemmaize': Lemmatizer.spacy},
        Lemm.nltk.value: {'lemmaize': Lemmatizer.nltk}
    }.get(lemm)
    return extract_words(sentence, **kwargs)


def doc_vec(model, doc):
    doc = [word for word in doc if word in model.wv.vocab]
    return np.mean(model[doc], axis=0)
