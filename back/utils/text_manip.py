import string
import decimal
import typing
from enum import IntEnum

import spacy
import nltk.data
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from num2words import num2words


__all__ = [
    'clear_new_lines',
    'clear_punct',
    'spacy_lemmatize',
    'nltk_lemmatize',
    'clear_stopwords',
    'num_to_words',
    'Lemmatizer',
    'extract_words'
]


def clear_new_lines(sentence: str) -> typing.List:
    res = sentence.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    res = ' '.join(res.split())
    return res.strip()


translator = str.maketrans('', '', string.punctuation)


def clear_punct(text: str) -> str:
    return text.translate(translator)


nlp = spacy.load('en', disable=['parser', 'ner'])


def spacy_lemmatize(sentence: str) -> typing.List:
    doc = nlp(sentence)
    return [token.lemma_ for token in doc if token.lemma_.strip()]


wnl = WordNetLemmatizer()


def nltk_lemmatize(sentence: str) -> typing.List:
    return [wnl.lemmatize(i, j[0].lower()) if j[0].lower() in ['a', 'n', 'v'] else
            wnl.lemmatize(i) for i, j in pos_tag(word_tokenize(sentence))]


def clear_stopwords(words: typing.List) -> typing.List:
    return [word for word in words if word not in stopwords.words('english')]


def num_to_words(words: typing.List) -> typing.List:
    res = []
    for word in words:
        try:
            changed = num2words(word)
        except (TypeError, decimal.InvalidOperation):
            changed = word
        res.append(changed)
    return res


Lemmatizer = IntEnum('Lemmatizer', 'spacy nltk', start=1)


def extract_words(
    sentence: str,
    *,
    clr_nl: bool = True,
    mk_lower: bool = True,
    clr_punct: bool = True,
    lemmaize: typing.Optional[Lemmatizer] = None,
    clr_stop: bool = True,
    change_num: bool = False
):
    if clr_nl:
        sentence = clear_new_lines(sentence)
    if mk_lower:
        sentence = sentence.lower()
    if clr_punct:
        sentence = clear_punct(sentence)
    words = []
    if lemmaize:
        if lemmaize == Lemmatizer.spacy:
            words = spacy_lemmatize(sentence)
        else:
            assert lemmaize == Lemmatizer.nltk
            words = nltk_lemmatize(sentence)
    else:
        words = word_tokenize(sentence)
    if clr_stop:
        words = clear_stopwords(words)
    if change_num:
        words = num2words(words)
    return words


tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


def split_sentences(text: str) -> typing.List:
    return tokenizer.tokenize(clear_new_lines(text))
