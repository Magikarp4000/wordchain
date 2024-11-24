import gensim.downloader as api
from gensim.models import Word2Vec

from utils import *


def download(model_name, save_name):
    model = api.load(model_name)
    model.save(f"{DIR_PATH}/models/{save_name}/{save_name}.model")

if __name__ == '__main__':
    download('word2vec-google-news-300', 'v2')
