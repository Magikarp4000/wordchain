import gensim.downloader as api
from gensim.models import Word2Vec
from gensim.models import KeyedVectors

import numpy as np
import json

from utils import *


def download(model_name, file_name):
    model = api.load(model_name)
    model.save(f"{DIR_PATH}/models/{file_name}/{file_name}.model")

def load(file_name):
    path = f"{DIR_PATH}/models/{file_name}/{file_name}.model"
    try:
        return Word2Vec.load(path)
    except AttributeError:
        keyed_vectors = KeyedVectors.load(path)
        model = Word2Vec()
        model.wv = keyed_vectors
        return model
    except FileNotFoundError:
        raise FileNotFoundError(f"{file_name}.model does not exist! Try running init.py first with the correct file name.")

def load_words():
    return open(f"{DIR_PATH}/datasets/words/en.txt", 'r').read().split('\n')

def load_embedding(file_name):
    path = f'{DIR_PATH}/models/{file_name}/{file_name}_embed.json'
    f = open(path, 'r')
    data = json.load(f)
    return {word: np.array(data[word]) for word in data}

def save_embedding(file_name, embedding):
    path = f'{DIR_PATH}/models/{file_name}/{file_name}_embed.json'
    f = open(path, 'w')
    data = json.dumps(embedding)
    f.write(data)
