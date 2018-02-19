"""
Script to generate data for user study.
Every participant should answer the questions based on the same data.
"""

import mediacloud
import logging.config
import json
import sys
import os
import numpy as np
#from gensim.models.keyedvectors import KeyedVectors
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = 'server/static'
MODEL_DIR = 'vector-models'

# set up logger
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("-------------------------------------------------------------------")

try:
    MC_API_KEY = os.environ['MC_API_KEY']
except KeyError:
    logging.error('You need to define the MC_API_KEY environment variable.')
    sys.exit(0)

mc = mediacloud.api.MediaCloud(MC_API_KEY)

try:
    TOPIC_ID = sys.argv[1]
except IndexError:
    logging.error('You need to specify a topic id as an argument.')
    sys.exit(0)

NUM_WORDS = 75
COS_SIM_THRESHOLD = 0.95  # approx. equal to cos(18 degs)


def filter_vocab(words, model):
    """
    Remove words not in model vocabulary or duplicates
    """
    to_be_removed = []
    unique_words = []
    for w in words:
        try:
            model[w['term'].strip()]
        except KeyError:
            to_be_removed.append(w)
            try:
                print 'Not in vocabulary:', w['term']
            except UnicodeEncodeError:
                print 'Not in vocabulary (Unicode Error)'

        if w['term'] not in unique_words:
            unique_words.append(w['term'])
        else:
            to_be_removed.append(w)

    for w in to_be_removed:
        words.remove(w)

    return words

if __name__ == '__main__':
    # Get top words
    top_words = mc.topicWordCount(TOPIC_ID, num_words=NUM_WORDS)

    # Load word2vec model
    model_file_path = os.path.join(BASE_DIR, MODEL_DIR, 'w2v-topic-model-{}'.format(TOPIC_ID))
    model = Word2Vec.load(model_file_path)

    # Remove words not in model vocab or duplicates
    top_words = filter_vocab(top_words, model)

    # Get 2D embeddings
    embeddings = [model[w['term'].strip()] for w in top_words]
    pca = PCA(n_components=2)
    two_d_embeddings = pca.fit_transform(np.asarray(embeddings))

    # Construct JSON (counts, embeddings, cosine similarities)
    results = []
    for i, word in enumerate(top_words):
        # find other words that are most similar to this word
        similar = []
        for other_word in top_words:
            if word['term'] != other_word['term']: # avoid double-counting
                # get similar words based on 2D embeddings
                temp = [{'term': x['term'], 'index': j} for j,x in enumerate(top_words)]
                other_i = filter(lambda x: x['term'] == other_word['term'], temp)[0]['index']
                this_i = filter(lambda x: x['term'] == word['term'], temp)[0]['index']
                sim_score_2d = np.asscalar(cosine_similarity(two_d_embeddings[this_i].reshape(1,-1),
                                                             two_d_embeddings[other_i].reshape(1,-1)))
                if sim_score_2d > COS_SIM_THRESHOLD:
                    similar.append({'text': other_word['term'], 'count': other_word['count'],
                                    'score': sim_score_2d})

        results.append({'text': word['term'], 'count': word['count'],
                        'similar': similar,'w2v_x': float(two_d_embeddings[i][0]),
                        'w2v_y': float(two_d_embeddings[i][1])})

    # Write json object to file
    output_file_path = os.path.join(BASE_DIR, OUTPUT_DIR, 'vizData.json')
    with open(output_file_path, 'w') as output:
    	output.write(json.dumps(results))
