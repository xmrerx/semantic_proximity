import uuid

import pandas as pd
from flask import Flask, jsonify, request, abort
from flask_cors import CORS, cross_origin
from gensim.models.doc2vec import Doc2Vec

from utils.text_manip import split_sentences
from utils.path import File
from utils.file_nav import (
    get_headlines, get_content, list_dir_files, get_sentence,
    save_content, SortBy, walk_sentences
)
from utils.conf import Conf
from train_utils.util import split_using


app = Flask(__name__)
cors = CORS(app)

conf = Conf.get(__file__, 'config.ini')

df_offsets = pd.read_pickle(conf.path('train', 'offsets.pkl'))

model = Doc2Vec.load(str(conf.path('train', conf.APP['use_name'])))


@app.route('/')
def hello_world():
    return 'It works!'


@cross_origin()
@app.route('/texts/<id>/compare', methods=['POST'])
def compare(id):
    if not request.json or 'sentence' not in request.json:
        abort(400)

    words = split_using(request.json['sentence'], conf.APP['use_lemm'])

    sim_docs = []
    unseen_sent = {}
    if int(conf.APP['compare_with_new_texts']):  # experimental / very slow
        sentences = walk_sentences(
            conf.path('texts'), conf.APP['ext'], without_file=id, split_line=False
        )
        for sentence_map in sentences:
            file_id, line_id, sentence = sentence_map
            cur_words = split_using(sentence, conf.APP['use_lemm'])
            unseen_sent[f"{file_id} {line_id}"] = sentence
            sim_docs.append((
                f"{file_id} {line_id}",
                float(model.docvecs.similarity_unseen_docs(
                    model,
                    words,
                    cur_words,
                    alpha=float(conf.TRAIN['alpha']),
                    min_alpha=float(conf.TRAIN['min_alpha']),
                    steps=int(conf.TRAIN['epochs'])
                ))
            ))
        if sim_docs:
            sim_docs.sort(key=lambda x: x[1], reverse=True)
            sim_docs = sim_docs[:int(conf.APP['sim_num'])]
    else:
        vector = model.infer_vector(
            words,
            steps=int(conf.TRAIN['epochs']),
            alpha=float(conf.TRAIN['alpha'])
        )
        sim_docs = model.docvecs.most_similar([vector], topn=int(conf.APP['sim_num']))

    resp = []
    doc_iter = 0
    for tag, sim_doc in sim_docs:
        file_id, sentence_row = tag.split()
        file = File(file_id, conf.APP['ext'])
        sentence = unseen_sent[tag] if tag in unseen_sent else None
        if not sentence:
            offset = df_offsets.loc[file.name]['offsets'][int(sentence_row)]
            sentence = get_sentence(conf.path('all_texts', str(file)), offset)
        resp.append({
            'text_id': file.name,
            'sentence_id': f'{doc_iter}-{sentence_row}',
            'sentece': sentence,
            'similarity': sim_doc
        })
        doc_iter += 1

    return jsonify(resp)


@cross_origin()
@app.route('/texts', methods=['POST'])
def add_text():
    if not request.json or 'text' not in request.json:
        abort(400)
    text = request.json['text']
    text_len = len(text.encode('utf-8'))
    if text_len > 1048576:
        return jsonify({'error': "Text size should be no bigger than 1Mb."})
    sentences = split_sentences(text)
    if len(sentences):
        new_file = File(uuid.uuid4(), conf.APP['ext'])
        save_content(conf.path('texts', str(new_file)), sentences)
    return jsonify({'file': new_file.name})


@cross_origin()
@app.route('/texts/<id>')
def get_text(id):
    file_name = str(File(id, conf.APP['ext']))
    content = ''
    try:
        content = get_content(conf.path('texts', file_name))
    except IOError:
        try:
            content = get_content(conf.path('all_texts', file_name))
        except IOError:
            abort(404)
    return jsonify(content)


@cross_origin()
@app.route('/texts')
def get_text_ids():
    file_names = list_dir_files(conf.path('texts'), SortBy.date_desc)
    files_with_titles = []
    for file_name in file_names:
        if file_name.startswith('.'):
            continue
        file = File(*file_name.split('.'))
        files_with_titles.append({
            'id': file.name,
            'title': get_headlines(conf.path('texts', str(file)))[0]
        })
    return jsonify(files_with_titles)


@cross_origin()
@app.errorhandler(404)
def page_not_found(error):
    abort(404)


if __name__ == '__main__':
    app.run(debug=True, host=conf.APP['host'], port=int(conf.APP['port']))
