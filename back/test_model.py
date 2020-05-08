import argparse
import logging
import pandas as pd
import sys  # noqa

from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.manifold import TSNE

from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure
from bokeh.io import save, output_notebook
from bokeh import resources

from utils.path import File
from utils.conf import Conf
from utils.file_nav import walk_sentences_simple, get_sentence
from train_utils.util import split_using


def show_similar(model, word, limit):
    print(f"words close to '{word}':")
    for word_num, word in enumerate(model.wv.most_similar(positive=[word])):
        if word_num >= limit:
            break
        print(f"  {word}")
    print('\n')


def most_frequent_words(sentences, max_features=1000):
    count_vectorizer = CountVectorizer(max_features=max_features)
    count_vectorizer.fit_transform(sentences)
    return sorted(count_vectorizer.vocabulary_, key=lambda x: x[1], reverse=True)


def draw_most_frequent(words, model, conf, name):
    output_notebook()
    words_top_vec = model.wv[words]

    tsne = TSNE(n_components=2, random_state=0)
    words_top_tsne = tsne.fit_transform(words_top_vec)
    p = figure(
        tools="pan,wheel_zoom,reset,save",
        toolbar_location="above",
        title="t-SNE for most common words"
    )

    source = ColumnDataSource(
        data=dict(x1=words_top_tsne[:, 0], x2=words_top_tsne[:, 1], names=list(words))
    )

    p.scatter(x="x1", y="x2", size=8, source=source)

    labels = LabelSet(
        x="x1",
        y="x2",
        text="names",
        y_offset=6,
        text_font_size="8pt",
        text_color="#555555",
        source=source,
        text_align='center')
    p.add_layout(labels)

    save(p, conf.path('train', f"{name}.html"), resources.INLINE, name)


def parse_args():
    parser = argparse.ArgumentParser(description='Test models.')
    parser.add_argument('-m', '--model', help='model: (d2v-dbow-no)')
    parser.add_argument('-l', '--limit', help='docs limit', type=int, default=1000)
    parser.add_argument('-q', '--questions', action='store_true',
                        help='check model with questions-words.txt')
    parser.add_argument('-t', '--tsne', action='store_true',
                        help='draw most frequent words')
    parser.add_argument('-s', '--simple', action='store_true',
                        help='check if model predict sentences in training set')

    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    conf = Conf.get(__file__, 'config.ini')

    args = parse_args()

    if not args.model:
        print('please, specify model')
        sys.exit()

    mod, alg, lemm = args.model.split('-')

    if mod:
        model = Doc2Vec.load(str(conf.path('train', f"{args.model}.model")))
    else:
        model = Word2Vec.load(str(conf.path('train', f"{args.model}.model")))

    logging.info('vocab: ' + ' | '.join(list(model.wv.vocab.keys())[:100]) + ' ...')

    if args.questions:
        score, sections = model.wv.evaluate_word_analogies(
            str(conf.path('train', 'questions-words.txt'))
        )
        correct, incorrect = len(sections[-1]['correct']), len(sections[-1]['incorrect'])
        all_words = correct + incorrect
        accuracy = round(float(correct * 100) / all_words, 2)
        print(f"{args.model} {model} {accuracy}% ({correct} of {all_words})")
        sys.exit()

    elif args.tsne:
        sentences = list(walk_sentences_simple(
            conf.path('train', lemm), conf.APP['ext'], split_line=False, stop=args.limit
        ))
        most_freq_words = most_frequent_words(sentences, 1000)

        most_freq_words_in_model = []
        for word in most_freq_words:
            try:
                model.wv[[word]]
                most_freq_words_in_model.append(word)
                # print(f'use {word}')
            except KeyError:
                # print(f'ignore {word}')
                pass

        for word in most_freq_words_in_model[:10]:
            show_similar(model, word, 5)

        draw_most_frequent(most_freq_words_in_model, model, conf, args.model)
    elif args.simple:
        df_offsets = pd.read_pickle(conf.path('train', 'offsets.pkl'))

        sentences = list(walk_sentences_simple(
            conf.path('train', lemm), conf.APP['ext'], stop=args.limit
        ))
        al = len(sentences)
        ok = 0
        for words in sentences:
            vector = model.infer_vector(
                words,
                steps=int(conf.TRAIN['epochs']),
                alpha=float(conf.TRAIN['alpha']))
            sim_docs = model.docvecs.most_similar([vector], topn=1)
            for tag, sim_doc in sim_docs:
                file_id, sentence_row = tag.split()
                file = File(file_id, conf.APP['ext'])
                offset = df_offsets.loc[file_id]['offsets'][int(sentence_row)]
                sentence = get_sentence(conf.path('all_texts', str(file)), offset)
                predict_words = split_using(sentence, lemm)
                if ' '.join(predict_words) == ' '.join(words):
                    ok += 1
                else:
                    logging.info(f"{tag} {sim_doc} || " +
                                 ' '.join(predict_words) + ' <> ' + ' '.join(words))
        print(f"{args.model} {model} " + str(round(ok / al, 2)) + f" ({ok} of {al})")

        # dbow| spacy  (14600 of 14906)
        # dbow| nltk   (14651 of 14906)
        # dbow| no     (14759 of 14906)

        # dm| spacy    (13220 of 14906)          13.99% (1372 of 9806)
        # dm| nltk     (13243 of 14906)          11.62% (1425 of 12264)
        # dm| no       (13761 of 14906)   quest: 13.39% (2100 of 15686)
